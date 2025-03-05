document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analyzeForm");
  const results = document.getElementById("results");
  const loading = document.getElementById("loading");
  const contributorTable = document.getElementById("contributorTable");
  let languageChart = null;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const data = {
      path: formData.get("path"),
      is_remote: formData.get("is_remote") === "on",
    };

    // Show loading state
    loading.classList.remove("hidden");
    results.classList.add("hidden");

    try {
      // Analyze repository
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze repository");
      }

      const stats = await response.json();

      // Get language distribution
      const langResponse = await fetch("/languages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!langResponse.ok) {
        throw new Error("Failed to get language distribution");
      }

      const { languages } = await langResponse.json();

      // Update contributor table
      updateContributorTable(stats);

      // Update language chart
      updateLanguageChart(languages);

      // Show results
      results.classList.remove("hidden");
    } catch (error) {
      alert("Error: " + error.message);
    } finally {
      loading.classList.add("hidden");
    }
  });

  function updateContributorTable(stats) {
    contributorTable.innerHTML = "";

    stats.forEach((stat) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${stat.name}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${stat.commit_count}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${stat.files_changed}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${stat.lines_added} / ${stat.lines_deleted}</td>
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

    // Create new chart
    languageChart = new Chart(ctx, {
      type: "pie",
      data: {
        labels: Object.keys(languages),
        datasets: [
          {
            data: Object.values(languages),
            backgroundColor: [
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40",
              "#FF6384",
              "#36A2EB",
              "#FFCE56",
              "#4BC0C0",
            ],
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: "right",
          },
        },
      },
    });
  }
});
