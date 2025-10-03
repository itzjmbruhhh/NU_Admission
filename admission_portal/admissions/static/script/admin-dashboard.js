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
  // Set chart width larger
  const programChartCanvas = document.getElementById("programChart");
  programChartCanvas.width = 600;
  programChartCanvas.height = 400;
  new Chart(programChartCanvas.getContext("2d"), {
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
