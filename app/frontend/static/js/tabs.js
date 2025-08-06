/**
 * Tab functionality for project detail pages
 * Replaces Bootstrap tab functionality with custom implementation
 */

export function initializeTabs() {
  // Only run on pages that have tabs
  const tabList = document.querySelector('[role="tablist"]');
  if (!tabList) {
    return;
  }

  const tabs = document.querySelectorAll('[data-toggle="tab"]');
  const tabPanes = document.querySelectorAll(".tab-pane");

  function showTab(targetTab, targetPane) {
    // Remove active classes from all tabs
    tabs.forEach((tab) => {
      tab.classList.remove(
        "border",
        "border-orange-accent",
        "border-b-0",
        "bg-slate-700",
        "-mb-px",
      );
      tab.setAttribute("aria-selected", "false");
    });

    // Hide all tab panes
    tabPanes.forEach((pane) => {
      pane.classList.add("hidden");
      pane.classList.remove("active");
    });

    // Activate the target tab
    targetTab.classList.add(
      "border",
      "border-orange-accent",
      "border-b-0",
      "bg-slate-700",
      "-mb-px",
    );
    targetTab.setAttribute("aria-selected", "true");

    // Show the target pane
    targetPane.classList.remove("hidden");
    targetPane.classList.add("active");
  }

  function handleTabClick(event) {
    event.preventDefault();

    const tab = event.currentTarget;
    const target = tab.getAttribute("href").substring(1); // Remove the #
    const targetPane = document.getElementById(target);

    if (targetPane) {
      showTab(tab, targetPane);

      // Update URL hash without jumping
      if (history.pushState) {
        history.pushState(null, null, "#" + target);
      } else {
        window.location.hash = target;
      }
    }
  }

  // Add click event listeners to all tabs
  tabs.forEach((tab) => {
    tab.addEventListener("click", handleTabClick);
  });

  // Handle initial page load with hash
  if (window.location.hash) {
    const hash = window.location.hash.substring(1);
    const targetPane = document.getElementById(hash);
    const targetTab = document.querySelector(`[href="#${hash}"]`);

    if (targetPane && targetTab) {
      showTab(targetTab, targetPane);
    }
  }

  // Handle browser back/forward navigation
  window.addEventListener("popstate", () => {
    if (window.location.hash) {
      const hash = window.location.hash.substring(1);
      const targetPane = document.getElementById(hash);
      const targetTab = document.querySelector(`[href="#${hash}"]`);

      if (targetPane && targetTab) {
        showTab(targetTab, targetPane);
      }
    } else {
      // No hash, show first tab
      const firstTab = tabs[0];
      const firstPane = tabPanes[0];
      if (firstTab && firstPane) {
        showTab(firstTab, firstPane);
      }
    }
  });
}
