//Scripts for registration.html
      // Complete Registration Form Script with Progress Bar and Paper Effects

      // Form Navigation State
      let currentSection = 0;
      const totalSections = 5;

      // Initialize everything when DOM is loaded
      document.addEventListener("DOMContentLoaded", function () {
        initializeForm();
        setupFormValidation();
        setupModalHandlers();
        setupLocationData();
        setupAddressSync();
        setupZipValidation();
        // loadDraftOnInit(); // <-- removed: do not auto-restore on every load
        clearDraftOnLoad(); // <-- added: only clear draft when the page was reloaded

        //  Auto-generate and set school year
        const today = new Date();
        const currentYear = today.getFullYear();
        const month = today.getMonth();

        // School year starts in July
        let startYear, endYear;
        if (month >= 6) {
          startYear = currentYear;
          endYear = currentYear + 1;
        } else {
          startYear = currentYear - 1;
          endYear = currentYear;
        }

        const schoolYear = `${startYear}-${endYear}`;
        const schoolYearEl = document.getElementById("schoolYear");
        if (schoolYearEl) {
          schoolYearEl.value = schoolYear;
        }
      });

      // Initialize the form navigation and progress
      function initializeForm() {
        updateProgress();
        updateNavigation();
        updateSectionVisibility();
      }

      // Section Navigation Functions
      function changeSection(direction) {
        const targetSection = currentSection + direction;

        if (direction > 0 && !validateCurrentSection()) {
          return;
        }

        if (targetSection >= 0 && targetSection < totalSections) {
          // Save current section data BEFORE moving forward
          if (direction > 0) {
            saveCurrentSectionData();
            // Mark current section as completed when moving forward
            markSectionCompleted(currentSection);
          }

          currentSection = targetSection;
          updateSectionVisibility();
          updateProgress();
          updateNavigation();

          // Scroll to the active section and focus its first form control
          const activeSectionEl = document.querySelector(
            `[data-section="${currentSection}"]`
          );
          if (activeSectionEl) {
            // small delay to allow any CSS enter animations/layout changes
            setTimeout(() => {
              activeSectionEl.scrollIntoView({
                behavior: "smooth",
                block: "center",
              });
              const focusable = activeSectionEl.querySelector(
                "input, select, textarea, button"
              );
              if (focusable) {
                try {
                  focusable.focus({ preventScroll: true });
                } catch (e) {
                  focusable.focus();
                }
              }
            }, 50);
          }
        }
      }

      function updateSectionVisibility() {
        const sections = document.querySelectorAll(".section");

        sections.forEach((section, index) => {
          section.classList.remove("active", "completed", "entering");

          if (index < currentSection) {
            section.classList.add("completed");
          } else if (index === currentSection) {
            section.classList.add("active");
            // Add entering animation for new sections
            if (index > 0) {
              section.classList.add("entering");
            }
          }
        });
      }

      function updateProgress() {
        const progressSteps = document.querySelectorAll(".progress-step");

        progressSteps.forEach((step, index) => {
          step.classList.remove("active", "completed");

          if (index < currentSection) {
            step.classList.add("completed");
          } else if (index === currentSection) {
            step.classList.add("active");
          }
        });
      }

      function updateNavigation() {
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        const sectionInfo = document.getElementById("sectionInfo");

        if (prevBtn) prevBtn.disabled = currentSection === 0;

        if (nextBtn) {
          if (currentSection === totalSections - 1) {
            nextBtn.style.display = "none";
          } else {
            nextBtn.style.display = "block";
          }
        }

        if (sectionInfo) {
          sectionInfo.textContent = `Step ${
            currentSection + 1
          } of ${totalSections}`;
        }
      }

      function markSectionCompleted(sectionIndex) {
        const section = document.querySelector(
          `[data-section="${sectionIndex}"]`
        );
        if (section) {
          section.classList.add("completed");
        }
      }

      // Validation Functions
      function validateCurrentSection() {
        const currentSectionEl = document.querySelector(
          `[data-section="${currentSection}"]`
        );
        if (!currentSectionEl) return true;

        const requiredFields = currentSectionEl.querySelectorAll("[required]");
        let hasErrors = false;
        let errorFields = [];

        requiredFields.forEach((field) => {
          if (!field.value.trim()) {
            hasErrors = true;
            field.classList.add("error");
            errorFields.push(field);
          } else {
            field.classList.remove("error");
          }
        });

        if (hasErrors) {
          showErrorModal(
            "Please fill in all required fields in this section before proceeding."
          );
          // Focus on first error field
          if (errorFields.length > 0) {
            errorFields[0].focus();
          }
          return false;
        }

        return true;
      }

      function showErrorModal(message) {
        const modal = document.getElementById("errorModal");
        const errorMessage = document.getElementById("errorMessage");
        if (modal && errorMessage) {
          errorMessage.textContent = message;
          modal.style.display = "block";
        }
      }

      // Setup Form Validation (Your existing validation logic)
      function setupFormValidation() {
        const formEl = document.getElementById("registrationForm");
        if (!formEl) return;

        formEl.addEventListener("submit", function (e) {
          // First validate current section
          if (!validateCurrentSection()) {
            e.preventDefault();
            return;
          }

          // Then validate entire form
          const requiredFields = formEl.querySelectorAll("[required]");
          let hasErrors = false;

          requiredFields.forEach((field) => {
            if (!field.value.trim()) {
              hasErrors = true;
              field.classList.add("error");
            } else {
              field.classList.remove("error");
            }
          });

          if (hasErrors) {
            e.preventDefault();
            showErrorModal(
              "Please fill in all required fields before submitting the form."
            );
          } else {
            // Allow normal form submission so Django receives the POST and saves the entry.
            // Clear local draft so partial data doesn't persist after real submit.
            localStorage.removeItem("registration_draft");
            // DO NOT call e.preventDefault() here — let the browser submit the form.
            // (If you want an AJAX submit instead, implement fetch()/XHR to your backend.)
          }
        });

        // Remove error class on input
        document.querySelectorAll("input, select").forEach((field) => {
          field.addEventListener("input", function () {
            this.classList.remove("error");
          });
        });
      }

      // New helper: save current section fields into localStorage as JSON
      function saveCurrentSectionData() {
        try {
          const sectionEl = document.querySelector(
            `[data-section="${currentSection}"]`
          );
          if (!sectionEl) return;
          const inputs = sectionEl.querySelectorAll(
            "input[name], select[name], textarea[name]"
          );
          const draft = JSON.parse(
            localStorage.getItem("registration_draft") || "{}"
          );
          inputs.forEach((i) => {
            // for checkboxes, store checked state instead of value
            if (i.type === "checkbox") {
              draft[i.name] = i.checked;
            } else {
              draft[i.name] = i.value || "";
            }
          });
          draft._lastSavedSection = currentSection;
          localStorage.setItem("registration_draft", JSON.stringify(draft));
          // console.log('Draft saved:', draft);
        } catch (err) {
          console.error("Failed to save draft:", err);
        }
      }

      // New helper: load draft from localStorage and populate fields
      function loadDraftOnInit() {
        try {
          const raw = localStorage.getItem("registration_draft");
          if (!raw) return;
          const draft = JSON.parse(raw);
          Object.keys(draft).forEach((name) => {
            if (name === "_lastSavedSection") return;
            const els = document.getElementsByName(name);
            if (!els || els.length === 0) return;
            const el = els[0];
            if (el.type === "checkbox") {
              el.checked = !!draft[name];
            } else {
              el.value = draft[name];
            }
            // trigger change for selects that might cascade (provinces/cities)
            if (el.tagName.toLowerCase() === "select") {
              el.dispatchEvent(new Event("change"));
            }
          });
          // restore section index if you want to jump back
          const last = draft._lastSavedSection;
          if (typeof last === "number") {
            currentSection = last;
            updateSectionVisibility();
            updateProgress();
            updateNavigation();
          }
          // console.log('Draft loaded', draft);
        } catch (err) {
          console.error("Failed to load draft:", err);
        }
      }

      // New helper: clear saved draft only when user refreshed the page
      function clearDraftOnLoad() {
        try {
          let isReload = false;
          // Modern Navigation Timing API
          if (
            performance &&
            typeof performance.getEntriesByType === "function"
          ) {
            const entries = performance.getEntriesByType("navigation");
            if (entries && entries.length) {
              isReload = entries[0].type === "reload";
            }
          }
          // Fallback for older browsers
          if (!isReload && performance && performance.navigation) {
            isReload = performance.navigation.type === 1; // 1 === reload
          }

          if (isReload) {
            localStorage.removeItem("registration_draft");
            // console.log('Cleared registration draft due to page reload');
          }
        } catch (err) {
          console.error("Failed to clear draft on load:", err);
        }
      }

      // Setup Modal Handlers (Your existing modal logic)
      function setupModalHandlers() {
        // Close modal functionality
        const closeBtn = document.querySelector(".close");
        if (closeBtn) {
          closeBtn.addEventListener("click", function () {
            const errorModal = document.getElementById("errorModal");
            if (errorModal) {
              errorModal.style.display = "none";
            }
          });
        }

        window.addEventListener("click", function (e) {
          const modal = document.getElementById("errorModal");
          if (e.target === modal) {
            modal.style.display = "none";
          }
        });

        // Progress step click handlers
        document.querySelectorAll(".progress-step").forEach((step, index) => {
          step.addEventListener("click", function () {
            // Only allow clicking on completed steps or current step
            if (
              index <= currentSection ||
              step.classList.contains("completed")
            ) {
              currentSection = index;
              updateSectionVisibility();
              updateProgress();
              updateNavigation();
            }
          });
        });

        // Check for success flag from Django backend — only on reload/redirect
        const successMeta = document.querySelector(
          'meta[name="submission_success"]'
        );
        const successFlag = successMeta && successMeta.content === "true";

        let isPageNavigation = false;
        if (performance && performance.getEntriesByType) {
          const entries = performance.getEntriesByType("navigation");
          if (entries.length > 0) {
            const navType = entries[0].type;
            // "navigate" = fresh visit, "reload" = user reload
            isPageNavigation = navType === "navigate" || navType === "reload";
          }
        }

        if (successFlag && isPageNavigation) {
          const successModal = document.getElementById("successModal");
          const modalOverlay = document.getElementById("modalOverlay");

          if (modalOverlay) {
            modalOverlay.style.display = "none"; // hide overlay
          }
          if (successModal) {
            successModal.style.display = "block"; // show success modal only
          }
        }
      }

      // Setup Location Data (Your existing PSGC API logic)
      function setupLocationData() {
        const REGION_API = "https://psgc.cloud/api/regions";

        function loadRegions(
          regionSelectId,
          provinceSelectId,
          citySelectId,
          brgySelectId
        ) {
          const regionEl = document.getElementById(regionSelectId);
          const provinceEl = document.getElementById(provinceSelectId);
          const cityEl = document.getElementById(citySelectId);
          const brgyEl = document.getElementById(brgySelectId);

          if (!regionEl || !provinceEl || !cityEl || !brgyEl) return;

          // Load regions
          fetch(REGION_API)
            .then((r) => r.json())
            .then((data) => {
              data.forEach((region) => {
                const opt = document.createElement("option");
                opt.value = region.name;
                opt.dataset.code = region.code;
                opt.textContent = region.name;
                regionEl.appendChild(opt);
              });
            })
            .catch((err) => console.error("Failed to load regions:", err));

          regionEl.addEventListener("change", () => {
            provinceEl.innerHTML = '<option value="">Select Province</option>';
            cityEl.innerHTML = '<option value="">Select City</option>';
            brgyEl.innerHTML = '<option value="">Select Barangay</option>';
            const regionCode = regionEl.selectedOptions[0]?.dataset.code;
            if (!regionCode) return;

            fetch(`https://psgc.cloud/api/regions/${regionCode}/provinces`)
              .then((r) => r.json())
              .then((provinces) => {
                provinces.forEach((p) => {
                  const opt = document.createElement("option");
                  opt.value = p.name;
                  opt.dataset.code = p.code;
                  opt.textContent = p.name;
                  provinceEl.appendChild(opt);
                });
              })
              .catch((err) => console.error("Failed to load provinces:", err));
          });

          provinceEl.addEventListener("change", () => {
            cityEl.innerHTML = '<option value="">Select City</option>';
            brgyEl.innerHTML = '<option value="">Select Barangay</option>';
            const provCode = provinceEl.selectedOptions[0]?.dataset.code;
            if (!provCode) return;

            fetch(
              `https://psgc.cloud/api/provinces/${provCode}/cities-municipalities`
            )
              .then((r) => r.json())
              .then((cities) => {
                cities.forEach((c) => {
                  const opt = document.createElement("option");
                  opt.value = c.name;
                  opt.dataset.code = c.code;
                  opt.textContent = c.name;
                  cityEl.appendChild(opt);
                });
              })
              .catch((err) => console.error("Failed to load cities:", err));
          });

          cityEl.addEventListener("change", () => {
            brgyEl.innerHTML = '<option value="">Select Barangay</option>';
            const cityCode = cityEl.selectedOptions[0]?.dataset.code;
            if (!cityCode) return;

            fetch(
              `https://psgc.cloud/api/cities-municipalities/${cityCode}/barangays`
            )
              .then((r) => r.json())
              .then((brgys) => {
                brgys.forEach((b) => {
                  const opt = document.createElement("option");
                  opt.value = b.name;
                  opt.dataset.code = b.code;
                  opt.textContent = b.name;
                  brgyEl.appendChild(opt);
                });
              })
              .catch((err) => console.error("Failed to load barangays:", err));
          });
        }

        // Load regions for current and permanent address
        loadRegions(
          "currentRegion",
          "presentProvince",
          "presentCity",
          "presentBarangay"
        );
        loadRegions(
          "permanentRegion",
          "permanentProvince",
          "permanentCity",
          "permanentBarangay"
        );

        // Load provinces for birth place and other province selects
        setupProvinceLoading();
      }

      function setupProvinceLoading() {
        const provinceApi = "https://psgc.cloud/api/provinces";

        const presentProvince = document.getElementById("presentProvince");
        const permanentProvince = document.getElementById("permanentProvince");
        const presentCity = document.getElementById("presentCity");
        const permanentCity = document.getElementById("permanentCity");
        const presentBarangay = document.getElementById("presentBarangay");
        const permanentBarangay = document.getElementById("permanentBarangay");
        const birthProvince = document.getElementById("birthProvince");
        const birthCity = document.getElementById("birthCity");

        // Load provinces into a select element
        function loadProvinces(selectEl) {
          if (!selectEl) return Promise.resolve();

          return fetch(provinceApi)
            .then((response) => response.json())
            .then((data) => {
              data.forEach((prov) => {
                const option = document.createElement("option");
                option.value = prov.name;
                option.dataset.code = prov.code;
                option.textContent = prov.name;
                selectEl.appendChild(option);
              });
            })
            .catch((err) => console.error("Failed to load provinces:", err));
        }

        // Load cities for a provinceCode into a citySelect
        function loadCities(provinceCode, citySelect) {
          if (!citySelect) return Promise.resolve();

          citySelect.innerHTML = '<option value="">Select City</option>';
          if (!provinceCode) return Promise.resolve();

          return fetch(
            `https://psgc.cloud/api/provinces/${provinceCode}/cities-municipalities`
          )
            .then((response) => response.json())
            .then((data) => {
              data.forEach((city) => {
                const option = document.createElement("option");
                option.value = city.name;
                option.dataset.code = city.code;
                option.textContent = city.name;
                citySelect.appendChild(option);
              });
            })
            .catch((err) => console.error("Failed to load cities:", err));
        }

        // Load barangays for a cityCode into a barangaySelect
        function loadBarangays(cityCode, barangaySelect) {
          if (!barangaySelect) return Promise.resolve();

          barangaySelect.innerHTML =
            '<option value="">Select Barangay</option>';
          if (!cityCode) return Promise.resolve();

          return fetch(
            `https://psgc.cloud/api/cities-municipalities/${cityCode}/barangays`
          )
            .then((response) => response.json())
            .then((data) => {
              data.forEach((brgy) => {
                const option = document.createElement("option");
                option.value = brgy.name;
                option.dataset.code = brgy.code;
                option.textContent = brgy.name;
                barangaySelect.appendChild(option);
              });
            })
            .catch((err) => console.error("Failed to load barangays:", err));
        }

        // Populate province selects
        Promise.all([
          loadProvinces(presentProvince),
          loadProvinces(permanentProvince),
          loadProvinces(birthProvince),
        ])
          .then(() => {
            // After provinces loaded, attach birthProvince change handler
            if (birthProvince && birthCity) {
              birthProvince.addEventListener("change", function () {
                const code = this.selectedOptions[0]?.dataset.code;
                loadCities(code, birthCity);
              });
            }
          })
          .catch(() => {
            /* errors already logged */
          });

        // Setup province change handlers
        if (presentProvince && presentCity) {
          presentProvince.addEventListener("change", function () {
            const code = this.selectedOptions[0]?.dataset.code;
            loadCities(code, presentCity);
          });
        }

        if (permanentProvince && permanentCity) {
          permanentProvince.addEventListener("change", function () {
            const code = this.selectedOptions[0]?.dataset.code;
            loadCities(code, permanentCity);
          });
        }

        // Setup city change handlers for barangays
        if (presentCity && presentBarangay) {
          presentCity.addEventListener("change", function () {
            const code = this.selectedOptions[0]?.dataset.code;
            loadBarangays(code, presentBarangay);
          });
        }

        if (permanentCity && permanentBarangay) {
          permanentCity.addEventListener("change", function () {
            const code = this.selectedOptions[0]?.dataset.code;
            loadBarangays(code, permanentBarangay);
          });
        }
      }

      // Setup Address Sync (Your existing "same as present" logic)
      function setupAddressSync() {
        const sameAsCheckbox = document.getElementById("sameAsPresent");
        if (!sameAsCheckbox) return;

        // Utility: wait until options are loaded into a <select>
        function waitForOptions(selectElement) {
          return new Promise((resolve) => {
            if (selectElement.options.length > 1) {
              resolve(); // already loaded
            } else {
              const observer = new MutationObserver(() => {
                if (selectElement.options.length > 1) {
                  observer.disconnect();
                  resolve();
                }
              });
              observer.observe(selectElement, { childList: true });
            }
          });
        }

        async function copyPresentToPermanent() {
          const presentAddress = document.getElementById("presentAddress");
          const presentZip = document.getElementById("presentZip");
          const currentRegion = document.getElementById("currentRegion");
          const presentProvince = document.getElementById("presentProvince");
          const presentCity = document.getElementById("presentCity");
          const presentBarangay = document.getElementById("presentBarangay");

          const permanentAddress = document.getElementById("permanentAddress");
          const permanentZip = document.getElementById("permanentZip");
          const permanentRegion = document.getElementById("permanentRegion");
          const permanentProvince =
            document.getElementById("permanentProvince");
          const permanentCity = document.getElementById("permanentCity");
          const permanentBarangay =
            document.getElementById("permanentBarangay");

          // Copy address + zip immediately
          permanentAddress.value = presentAddress.value;
          permanentZip.value = presentZip.value;

          // Copy region → then wait for provinces to load
          permanentRegion.value = currentRegion.value;
          permanentRegion.dispatchEvent(new Event("change"));
          await waitForOptions(permanentProvince);

          // Copy province → then wait for cities
          permanentProvince.value = presentProvince.value;
          permanentProvince.dispatchEvent(new Event("change"));
          await waitForOptions(permanentCity);

          // Copy city → then wait for barangays
          permanentCity.value = presentCity.value;
          permanentCity.dispatchEvent(new Event("change"));
          await waitForOptions(permanentBarangay);

          // Finally copy barangay
          permanentBarangay.value = presentBarangay.value;
        }

        function clearPermanentFields() {
          const permanentAddress = document.getElementById("permanentAddress");
          const permanentZip = document.getElementById("permanentZip");
          const permanentRegion = document.getElementById("permanentRegion");
          const permanentProvince =
            document.getElementById("permanentProvince");
          const permanentCity = document.getElementById("permanentCity");
          const permanentBarangay =
            document.getElementById("permanentBarangay");

          if (permanentAddress) permanentAddress.value = "";
          if (permanentZip) permanentZip.value = "";
          if (permanentRegion) permanentRegion.value = "";
          if (permanentProvince) permanentProvince.value = "";
          if (permanentCity) {
            permanentCity.innerHTML = '<option value="">Select City</option>';
            permanentCity.value = "";
          }
          if (permanentBarangay) {
            permanentBarangay.innerHTML =
              '<option value="">Select Barangay</option>';
            permanentBarangay.value = "";
          }
        }

        sameAsCheckbox.addEventListener("change", function () {
          if (this.checked) {
            copyPresentToPermanent();
          } else {
            clearPermanentFields();
          }
        });

        // Keep permanent synced while checkbox is checked
        ["presentAddress", "presentZip"].forEach((id) => {
          const element = document.getElementById(id);
          if (element) {
            element.addEventListener("input", () => {
              if (sameAsCheckbox.checked) copyPresentToPermanent();
            });
          }
        });

        // Sync when present address fields change
        const presentProvince = document.getElementById("presentProvince");
        const presentCity = document.getElementById("presentCity");
        const presentBarangay = document.getElementById("presentBarangay");
        const currentRegion = document.getElementById("currentRegion");

        if (presentProvince) {
          presentProvince.addEventListener("change", () => {
            if (sameAsCheckbox.checked) copyPresentToPermanent();
          });
        }

        if (presentCity) {
          presentCity.addEventListener("change", () => {
            if (sameAsCheckbox.checked) copyPresentToPermanent();
          });
        }

        if (presentBarangay) {
          presentBarangay.addEventListener("change", () => {
            if (sameAsCheckbox.checked) copyPresentToPermanent();
          });
        }

        if (currentRegion) {
          currentRegion.addEventListener("change", () => {
            if (sameAsCheckbox.checked) copyPresentToPermanent();
          });
        }
      }

      // Setup Zip Code Validation (Your existing zip validation)
      function setupZipValidation() {
        ["presentZip", "permanentZip"].forEach((id) => {
          const zipInput = document.getElementById(id);
          if (zipInput) {
            zipInput.addEventListener("input", function () {
              this.value = this.value.replace(/\D/g, "").slice(0, 4); // remove non-digits and limit to 4 chars
            });
          }
        });
      }

      // Make changeSection function globally available for onclick handlers
      window.changeSection = changeSection;

      // Mobile number input restriction to digits only and max length
      document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".mobile-number").forEach((input) => {
          input.addEventListener("input", function () {
            // Allow only digits and limit to 11 characters
            this.value = this.value.replace(/\D/g, "").slice(0, 11);
          });
        });
      });

      function closeModal() {
        document.getElementById("modalOverlay").style.display = "none";
      }

      // Allow closing by clicking outside modal
      document.addEventListener("click", function (e) {
        if (e.target.id === "modalOverlay") {
          closeModal();
        }
      });

// End of registration.html script

