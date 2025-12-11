/**
 * Feedback widget for GLM Tutorial pages
 * Generates GitHub issue links with page context pre-filled
 */
(function() {
  // Get current page info from URL path
  function getPageInfo() {
    const path = window.location.pathname;
    const parts = path.split('/').filter(p => p);

    // Extract tutorial number and page name
    let tutorial = 'Index';
    let page = 'index';

    // Look for tutorial folder pattern (01-gaussian, 02-logistic, etc.)
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].match(/^\d{2}-/)) {
        tutorial = parts[i];
        if (parts[i + 1]) {
          page = parts[i + 1].replace('.html', '');
        }
        break;
      }
    }

    // Map tutorial folder to friendly name
    const tutorialNames = {
      '01-gaussian': 'Tutorial 1: Gaussian',
      '02-logistic': 'Tutorial 2: Binomial',
      '03-poisson': 'Tutorial 3: Poisson',
      '04-negbin': 'Tutorial 4: Negative Binomial',
      '05-gamma': 'Tutorial 5: Gamma'
    };

    const friendlyTutorial = tutorialNames[tutorial] || tutorial;

    return {
      tutorial: friendlyTutorial,
      page: page,
      fullPath: path
    };
  }

  // Generate GitHub issue URL with pre-filled content
  function getBugReportUrl() {
    const info = getPageInfo();
    const title = encodeURIComponent(`[Bug] ${info.tutorial} - ${info.page}`);
    const body = encodeURIComponent(
      `## Page/Tutorial\n${info.tutorial} > ${info.page}\n` +
      `URL: ${window.location.href}\n\n` +
      `## What happened?\n\n\n` +
      `## What did you expect to happen?\n\n\n` +
      `## Steps to reproduce\n1. \n2. \n3. \n`
    );
    return `https://github.com/JonMinton/glm-dashboard-explainer/issues/new?template=bug_report.md&title=${title}&body=${body}`;
  }

  function getFeatureRequestUrl() {
    const info = getPageInfo();
    const title = encodeURIComponent(`[Feature] `);
    const body = encodeURIComponent(
      `## Context\nSuggestion from: ${info.tutorial} > ${info.page}\n\n` +
      `## Summary\n\n\n` +
      `## Problem or motivation\n\n\n` +
      `## Suggested solution\n\n`
    );
    return `https://github.com/JonMinton/glm-dashboard-explainer/issues/new?template=feature_request.md&title=${title}&body=${body}`;
  }

  // Create and inject the feedback widget
  function createWidget() {
    // Create container
    const widget = document.createElement('div');
    widget.className = 'feedback-widget';
    widget.innerHTML = `
      <style>
        .feedback-widget {
          position: fixed;
          bottom: 20px;
          right: 20px;
          z-index: 1000;
        }
        .feedback-toggle {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: #2c3e50;
          color: white;
          border: none;
          cursor: pointer;
          font-size: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
          transition: transform 0.2s, background 0.2s;
        }
        .feedback-toggle:hover {
          transform: scale(1.1);
          background: #34495e;
        }
        .feedback-menu {
          display: none;
          position: absolute;
          bottom: 60px;
          right: 0;
          background: white;
          border-radius: 8px;
          box-shadow: 0 4px 16px rgba(0,0,0,0.15);
          overflow: hidden;
          min-width: 180px;
        }
        .feedback-menu.show {
          display: block;
          animation: fadeInUp 0.2s ease;
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .feedback-menu a {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 12px 16px;
          text-decoration: none;
          color: #333;
          font-size: 14px;
          border-bottom: 1px solid #eee;
          transition: background 0.2s;
        }
        .feedback-menu a:last-child {
          border-bottom: none;
        }
        .feedback-menu a:hover {
          background: #f8f9fa;
        }
        .feedback-menu .icon {
          font-size: 16px;
        }
        .feedback-menu .bug { color: #e74c3c; }
        .feedback-menu .feature { color: #3498db; }
      </style>
      <div class="feedback-menu" id="feedbackMenu">
        <a href="${getBugReportUrl()}" target="_blank">
          <span class="icon bug">🐛</span>
          Report a Bug
        </a>
        <a href="${getFeatureRequestUrl()}" target="_blank">
          <span class="icon feature">💡</span>
          Suggest Feature
        </a>
      </div>
      <button class="feedback-toggle" id="feedbackToggle" title="Give Feedback">
        ?
      </button>
    `;

    document.body.appendChild(widget);

    // Toggle menu on button click
    const toggle = document.getElementById('feedbackToggle');
    const menu = document.getElementById('feedbackMenu');

    toggle.addEventListener('click', () => {
      menu.classList.toggle('show');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!widget.contains(e.target)) {
        menu.classList.remove('show');
      }
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createWidget);
  } else {
    createWidget();
  }
})();
