document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analyzeForm");
  const results = document.getElementById("results");
  const loading = document.getElementById("loading");
  const contributorTable = document.getElementById("contributorTable");
  const contributorSearch = document.getElementById("contributorSearch");
  const repoNameElement = document.getElementById("repoName");
  const totalLanguagesElement = document.getElementById("totalLanguages");
  const totalContributorsElement = document.getElementById("totalContributors");
  const totalCommitsElement = document.getElementById("totalCommits");

  let languageChart = null;
  let contributionChart = null;
  let contributorsData = [];

  // GitHub-inspired colors for charts
  const chartColors = [
    "#2ea44f", // GitHub green
    "#0366d6", // GitHub blue
    "#6f42c1", // GitHub purple
    "#d73a49", // GitHub red
    "#f66a0a", // GitHub orange
    "#6a737d", // GitHub gray
    "#22863a", // GitHub dark green
    "#005cc5", // GitHub dark blue
    "#5a32a3", // GitHub dark purple
    "#cb2431", // GitHub dark red
    "#e36209", // GitHub dark orange
    "#24292e", // GitHub dark gray
  ];

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {
      path: formData.get("path"),
      is_remote: true, // Always true for web version
    };

    // Extract repo name from URL for display
    const repoUrl = data.path;
    const repoNameMatch = repoUrl.match(/github\.com\/([^\/]+)\/([^\/]+)/);

    if (repoNameMatch && repoNameMatch.length >= 3) {
      const owner = repoNameMatch[1];
      const repo = repoNameMatch[2];
      repoNameElement.textContent = `${owner}/${repo}`;
    } else {
      repoNameElement.textContent = repoUrl;
    }

    // Show loading state
    loading.classList.remove("hidden");
    results.classList.add("hidden");

    // Analyze repository
    fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((errorData) => {
            throw new Error(errorData.detail || "Failed to analyze repository");
          });
        }
        return response.json();
      })
      .then((stats) => {
        contributorsData = stats; // Store for filtering

        // Get language distribution
        return fetch("/languages", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });
      })
      .then((langResponse) => {
        if (!langResponse.ok) {
          throw new Error("Failed to get language distribution");
        }
        return langResponse.json();
      })
      .then(({ languages }) => {
        // Update summary stats
        updateSummaryStats(contributorsData, languages);

        // Update contributor table
        updateContributorTable(contributorsData);

        // Update language chart
        updateLanguageChart(languages);

        // Update contribution impact chart
        updateContributionChart(contributorsData);

        // Show results
        results.classList.remove("hidden");
      })
      .catch((error) => {
        showError(error.message);
      })
      .finally(() => {
        loading.classList.add("hidden");
      });
  });

  function updateSummaryStats(stats, languages) {
    // Update total languages
    totalLanguagesElement.textContent = Object.keys(languages).length;

    // Update total contributors
    totalContributorsElement.textContent = stats.length;

    // Calculate total commits
    const totalCommits = stats.reduce(
      (sum, contributor) => sum + contributor.commit_count,
      0
    );
    totalCommitsElement.textContent = totalCommits.toLocaleString();
  }

  function updateContributorTable(stats) {
    contributorTable.innerHTML = "";

    stats.forEach((stat) => {
      const row = document.createElement("tr");
      row.className = "contributor-row hover:bg-gray-50";

      // Calculate percentage for progress bar
      const percentage = stat.percentage.toFixed(1);

      row.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
          <div class="flex items-center">
            <div class="flex-shrink-0 h-10 w-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 font-medium">
              ${stat.name.charAt(0).toUpperCase()}
            </div>
            <div class="ml-4">
              <div class="text-sm font-medium text-gray-900">${stat.name}</div>
              <div class="text-sm text-gray-500">${stat.email}</div>
            </div>
          </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
            ${stat.commit_count}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <span class="badge badge-added">${stat.lines_added}</span>
          <span class="badge badge-deleted">${stat.lines_deleted}</span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          ${stat.files_changed}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
          <div class="flex items-center">
            <div class="w-full bg-gray-200 rounded-full h-2.5 mr-2 max-w-[100px]">
              <div class="bg-green-600 h-2.5 rounded-full" style="width: ${percentage}%"></div>
            </div>
            <span>${percentage}%</span>
          </div>
        </td>
      `;

      contributorTable.appendChild(row);
    });
  }

  function updateLanguageChart(languages) {
    const ctx = document.getElementById("languageChart").getContext("2d");

    // Destroy existing chart if it exists
    if (languageChart) {
      languageChart.destroy();
    }

    // Get language names and values
    const languageNames = Object.keys(languages);
    const languageValues = Object.values(languages);

    // Create new chart
    languageChart = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: languageNames,
        datasets: [
          {
            data: languageValues,
            backgroundColor: chartColors.slice(0, languageNames.length),
            borderColor: "rgba(255, 255, 255, 0.8)",
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "right",
            labels: {
              boxWidth: 12,
              padding: 15,
              font: {
                size: 11,
              },
            },
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.raw;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = Math.round((value / total) * 100);
                return `${label}: ${percentage}% (${value} bytes)`;
              },
            },
          },
        },
        cutout: "70%",
        animation: {
          animateScale: true,
          animateRotate: true,
        },
      },
    });
  }

  function updateContributionChart(stats) {
    const ctx = document.getElementById("contributionChart").getContext("2d");

    // Destroy existing chart if it exists
    if (contributionChart) {
      contributionChart.destroy();
    }

    // Sort contributors by total changes (descending)
    const sortedContributors = [...stats]
      .sort(
        (a, b) =>
          b.lines_added + b.lines_deleted - (a.lines_added + a.lines_deleted)
      )
      .slice(0, 5); // Only show top 5 contributors

    // Create new chart
    contributionChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: sortedContributors.map((c) => c.name),
        datasets: [
          {
            label: "Lines Added",
            data: sortedContributors.map((c) => c.lines_added),
            backgroundColor: "rgba(40, 167, 69, 0.7)",
            borderColor: "rgba(40, 167, 69, 1)",
            borderWidth: 1,
          },
          {
            label: "Lines Deleted",
            data: sortedContributors.map((c) => c.lines_deleted),
            backgroundColor: "rgba(215, 58, 73, 0.7)",
            borderColor: "rgba(215, 58, 73, 1)",
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: false,
            grid: {
              display: false,
            },
          },
          y: {
            stacked: false,
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
          },
        },
        plugins: {
          legend: {
            position: "top",
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
      },
    });
  }

  // Search functionality for contributors
  if (contributorSearch) {
    contributorSearch.addEventListener("input", (e) => {
      const searchTerm = e.target.value.toLowerCase();

      if (!contributorsData.length) return;

      const filteredContributors = searchTerm
        ? contributorsData.filter(
            (c) =>
              c.name.toLowerCase().includes(searchTerm) ||
              c.email.toLowerCase().includes(searchTerm)
          )
        : contributorsData;

      updateContributorTable(filteredContributors);
    });
  }

  function showError(message) {
    const errorDiv = document.createElement("div");
    errorDiv.className =
      "bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-8";
    errorDiv.innerHTML = `
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <p class="text-sm">Error: ${message}</p>
        </div>
      </div>
    `;

    // Insert error before results
    const container = document.querySelector(".container");
    container.insertBefore(errorDiv, results);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      errorDiv.remove();
    }, 5000);
  }
});
