if (
  window.location.pathname.includes("adminDash") ||
  window.location.search.match(/(program=|status=|school_year=|page=)/)
) {
  showSection("search");
}
// Activate Student Records tab if filter or pagination is present
if (window.location.search.match(/(program=|status=|school_year=|page=)/)) {
  showSection("search");
}
document.addEventListener("DOMContentLoaded", function () {
  // ==========================
  // Section Tab Activation on Page Load (pagination support)
  // ==========================
  if (window.location.search.includes("page=")) {
    showSection("search");
  }

  // ==========================
  // Academic Year Distribution (actual data)
  // ==========================
  // Use json_script data for academic year chart
  let academicYearLabels = JSON.parse(
    document.getElementById("academic-year-labels").textContent
  );
  let academicYearData = JSON.parse(
    document.getElementById("academic-year-data").textContent
  );
  // Generate a color for each year
  function getColorPalette(n) {
    const palette = [
      "#1e40af",
      "#FFD700",
      "#059669",
      "#0891b2",
      "#dc2626",
      "#e65959",
      "#6366f1",
      "#f59e42",
      "#10b981",
      "#f43f5e",
    ];
    let colors = [];
    for (let i = 0; i < n; i++) {
      colors.push(palette[i % palette.length]);
    }
    return colors;
  }
  new Chart(document.getElementById("yearChart").getContext("2d"), {
    type: "bar",
    data: {
      labels: academicYearLabels,
      datasets: [
        {
          label: "No. of Students",
          data: academicYearData,
          backgroundColor: getColorPalette(academicYearLabels.length),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
    },
  });

  // ==========================
  // Program Popularity (Pie Chart)
  // ==========================
  // Program Popularity Pie Chart (actual data)
  let programLabelsRaw = JSON.parse(
    document.getElementById("program-labels").textContent
  );
  let programData = JSON.parse(
    document.getElementById("program-data").textContent
  );
  // Labels already abbreviated server-side
  let programLabels = programLabelsRaw;
  let programColors = [
    "#1e40af",
    "#FFD700",
    "#059669",
    "#0891b2",
    "#dc2626",
    "#e65959",
    "#6366f1",
    "#f59e42",
    "#10b981",
    "#f43f5e",
  ];
  let pieColors = [];
  for (let i = 0; i < programLabels.length; i++) {
    pieColors.push(programColors[i % programColors.length]);
  }
  // Set chart width larger and keep instance for updates
  const programChartCanvas = document.getElementById("programChart");
  programChartCanvas.width = 600;
  programChartCanvas.height = 400;
  window.programChartInstance = new Chart(programChartCanvas.getContext("2d"), {
    type: "pie",
    data: {
      labels: programLabels,
      datasets: [
        {
          data: programData,
          backgroundColor: pieColors,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            font: {
              size: 14,
            },
          },
        },
      },
    },
  });

  // Helper to compute top N entries from labels+data
  function getTopN(labels, data, n) {
    // build array of {label, value}
    const arr = labels.map((l, i) => ({ label: l, value: Number(data[i]) || 0 }));
    arr.sort((a, b) => b.value - a.value);
    return arr.slice(0, n);
  }

  // Helper to update the pie chart for top N and include 'Other' slice
  let currentTopN = null; // null means show all
  function updatePieForTopN(n) {
    if (!n) {
      // show all
      window.programChartInstance.data.labels = programLabels;
      window.programChartInstance.data.datasets[0].data = programData;
      window.programChartInstance.data.datasets[0].backgroundColor = pieColors;
      currentTopN = null;
      window.programChartInstance.update();
      return;
    }
    const top = getTopN(programLabels, programData, n);
    const topLabels = top.map((t) => t.label);
    const topValues = top.map((t) => t.value);
    const total = programData.reduce((s, v) => s + (Number(v) || 0), 0);
    const topSum = topValues.reduce((s, v) => s + v, 0);
    const other = Math.max(0, total - topSum);
    const labels = [...topLabels];
    const values = [...topValues];
    const colors = pieColors.slice(0, topLabels.length);
    if (other > 0) {
      labels.push('Other programs');
      values.push(other);
      colors.push('#9ca3af');
    }
    window.programChartInstance.data.labels = labels;
    window.programChartInstance.data.datasets[0].data = values;
    window.programChartInstance.data.datasets[0].backgroundColor = colors;
    currentTopN = n;
    window.programChartInstance.update();
  }

    // --- Top Courses panel population and wiring ---
    function populateTopCourses(n) {
      // Prefer dropdown list if available
      const container = document.getElementById('topCoursesList');
      if (!container) return;
      const total = programData.reduce((s, v) => s + (Number(v) || 0), 0);
      const top = getTopN(programLabels, programData, n);
      container.innerHTML = '';
      top.forEach((t, idx) => {
        const percent = total > 0 ? ((t.value / total) * 100).toFixed(1) : '0.0';
        const item = document.createElement('div');
        item.style.display = 'flex';
        item.style.justifyContent = 'space-between';
        item.style.alignItems = 'center';
        item.style.padding = '6px 4px';
        item.style.borderRadius = '6px';
        item.style.cursor = 'default';
        item.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px">
            <span style="width:10px;height:10px;border-radius:50%;display:inline-block;background:${pieColors[idx]};"></span>
            <span style="font-weight:600;color:#0f172a">${t.label}</span>
          </div>
          <div style="text-align:right;color:#6b7280">${t.value} <small style=\"color:#9ca3af\">(${percent}%)</small></div>
        `;
        container.appendChild(item);
      });

      const topSum = top.reduce((s, x) => s + x.value, 0);
      const other = total - topSum;
      if (other > 0) {
        const percent = total > 0 ? ((other / total) * 100).toFixed(1) : '0.0';
        const otherItem = document.createElement('div');
        otherItem.style.display = 'flex';
        otherItem.style.justifyContent = 'space-between';
        otherItem.style.alignItems = 'center';
        otherItem.style.padding = '6px 4px';
        otherItem.style.borderRadius = '6px';
        otherItem.style.marginTop = '6px';
        otherItem.style.borderTop = '1px dashed rgba(0,0,0,0.06)';
        otherItem.innerHTML = `
          <div style="display:flex;align-items:center;gap:8px">
            <span style="width:10px;height:10px;border-radius:50%;display:inline-block;background:#9ca3af;"></span>
            <span style="font-weight:600;color:#0f172a">Other programs</span>
          </div>
          <div style="text-align:right;color:#6b7280">${other} <small style=\"color:#9ca3af\">(${percent}%)</small></div>
        `;
        container.appendChild(otherItem);
      }
    }

    // Wire Top 5 / Top 10 buttons to update pie and dropdown list
    const top5Btn = document.getElementById('top5Btn');
    const top10Btn = document.getElementById('top10Btn');
    if (top5Btn) {
      top5Btn.addEventListener('click', function () {
        updatePieForTopN(5);
        populateTopCourses(5);
      });
    }
    if (top10Btn) {
      top10Btn.addEventListener('click', function () {
        updatePieForTopN(10);
        populateTopCourses(10);
      });
    }

    // Populate dropdown list on first paint (so it has content)
    populateTopCourses(5);

    // Dropdown toggle behavior (if dropdown exists)
    const topCoursesToggle = document.getElementById('topCoursesToggle');
    const topCoursesDropdown = document.getElementById('topCoursesDropdown');
    if (topCoursesToggle && topCoursesDropdown) {
      topCoursesToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        const shown = topCoursesDropdown.style.display === 'block';
        topCoursesDropdown.style.display = shown ? 'none' : 'block';
    // refresh content when showing
    if (!shown) populateTopCourses(currentTopN || 5);
      });

      // Close on outside click
      document.addEventListener('click', function (ev) {
        if (!topCoursesDropdown.contains(ev.target) && ev.target !== topCoursesToggle) {
          topCoursesDropdown.style.display = 'none';
        }
      });
    }

  // ==========================
  // Admission Success Rate
  // ==========================
  // Admission Success Rate Chart (actual data)
  let admissionLabels = JSON.parse(
    document.getElementById("admission-labels").textContent
  );
  let admissionData = JSON.parse(
    document.getElementById("admission-data").textContent
  );
  let admissionColors = ["#059669", "#e65959"];
  new Chart(document.getElementById("admissionChart").getContext("2d"), {
    type: "bar",
    data: {
      labels: admissionLabels,
      datasets: [
        {
          label: "Applicants",
          data: admissionData,
          backgroundColor: admissionColors,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
    },
  });
});

// Chart toggle buttons
document.querySelectorAll(".chart-btn").forEach((btn) => {
  btn.addEventListener("click", function () {
    document
      .querySelectorAll(".chart-btn")
      .forEach((b) => b.classList.remove("active"));
    this.classList.add("active");

    programChart.destroy();
    programChartType = this.dataset.chart;
    programChart = new Chart(programCtx, {
      type: programChartType,
      data: {
        labels: ["BSCS", "BSIT", "BSCE", "BSBA"],
        datasets: [
          {
            data: [80, 70, 60, 40],
            backgroundColor: ["#1e40af", "#059669", "#FFD700", "#0891b2"],
          },
        ],
      },
      options:
        programChartType === "bar"
          ? { scales: { y: { beginAtZero: true } } }
          : {},
    });
  });
});

// ==========================
// Gender Distribution
// ==========================
new Chart(document.getElementById("genderChart").getContext("2d"), {
  type: "pie",
  data: {
    labels: ["Male", "Female"],
    datasets: [
      {
        data: [220, 230],
        backgroundColor: ["#1e40af", "#FFD700"],
      },
    ],
  },
});

// ==========================
// Admission Success Rate
// ==========================
new Chart(document.getElementById("admissionChart").getContext("2d"), {
  type: "bar",
  data: {
    labels: ["Approved", "Pending", "Rejected"],
    datasets: [
      {
        label: "Applicants",
        data: [300, 100, 50],
        backgroundColor: ["#059669", "#FFD700", "#dc2626"],
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: { y: { beginAtZero: true } },
  },
});

// ==========================
// Section Tab Switching
// ==========================
function showSection(id) {
  document.querySelectorAll(".section-content").forEach((sec) => {
    sec.classList.remove("active");
  });
  document.getElementById(id).classList.add("active");

  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) => btn.classList.remove("active"));
  document
    .querySelector(`.tab-btn[onclick="showSection('${id}')"]`)
    .classList.add("active");
}
window.showSection = showSection;

// ==========================
// Logout (placeholder)
// ==========================
function logout() {
  window.location.href = "/";
}
window.logout = logout;
// ==========================
// Search & Reset
// ==========================
document.getElementById("searchBtn").addEventListener("click", function () {
  const nameSearch = document.getElementById("nameSearch").value.toLowerCase();
  const programFilter = document.getElementById("programFilter").value;
  const chanceSearch = document.getElementById("chanceSearch").value;

  let found = false;
  document.querySelectorAll("#studentTable tbody tr").forEach((row) => {
    const name = row.cells[2].innerText.toLowerCase();
    const program = row.cells[3].innerText;
    const chance = row.cells[5].innerText;

    let match = true;
    if (nameSearch && !name.includes(nameSearch)) match = false;
    if (programFilter && !program.includes(programFilter)) match = false;
    if (chanceSearch && !chance.includes(chanceSearch)) match = false;

    row.style.display = match ? "" : "none";
    if (match) found = true;
  });

  document.getElementById("noResults").style.display = found ? "none" : "block";
});

document.getElementById("resetBtn").addEventListener("click", function () {
  document.getElementById("nameSearch").value = "";
  document.getElementById("programFilter").value = "";
  document.getElementById("chanceSearch").value = "";

  document
    .querySelectorAll("#studentTable tbody tr")
    .forEach((row) => (row.style.display = ""));
  document.getElementById("noResults").style.display = "none";
});

// ==========================
// Select All Checkboxes
// ==========================
document.getElementById("selectAll").addEventListener("change", function () {
  const checked = this.checked;
  document
    .querySelectorAll(".row-select")
    .forEach((cb) => (cb.checked = checked));
});
