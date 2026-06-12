# Tiers 2-4: Decision Points and Rough Scope

These tiers should be planned in detail only after Tier 1 is complete and committed.
Each tier has open questions that affect scope and approach.

---

## Tier 2: Connect the Pieces

### Goal
Make the site feel like a cohesive whole rather than two separate projects
(optimization demos + GLM tutorials) that happen to share a domain.

### Decision points before planning
1. **JonStats integration depth**: Just add links? Or restructure the index page to
   position the dashboard as "the interactive part of JonStats"? The latter would
   require agreement on how the two sites relate.
2. **Which tutorial gets the interactive fitting demo?** Gaussian is simplest
   (closed-form solution + LL surface is a simple bowl). But Logistic might be
   more compelling (no closed-form, IRLS iteration visible). Pick one to prototype.
3. **Bridge page vs integrated approach**: A standalone "bridge" page explaining
   terrain=log-likelihood, or embed the explanation directly into the first
   tutorial's fitting page? The latter is more seamless but harder.
4. **Data embedding**: Interactive fitting needs data in the page. How much data?
   Full dataset (~300 rows for heart) or a subset (~30 rows for speed)?

### Rough scope
- 2.1 (JonStats links): ~30 minutes, trivial
- 2.2 (interactive fitting): 1-2 sessions, significant new JS
- 2.3 (bridge explanation): ~1 session, mostly content

---

## Tier 3: Fill Gaps

### Goal
Address structural omissions that limit the site's pedagogical value.

### Decision points before planning
1. **CSS extraction strategy**: Write a script to do it automatically
   (`scripts/build/extract-css.py` already exists but may need updating)?
   Or manual extraction for more control? This touches every file so timing
   matters — do it during a quiet period.
2. **Diagnostics scope**: Just a static residual plot for Tutorial 3, or a
   reusable diagnostic component that works across tutorials? The latter is
   more work but pays off if more tutorials are added.
3. **Simulation page scope**: Full King-Tomz-Wittenberg quantities of interest
   (expected values, predicted values, first differences with uncertainty)?
   Or just a simple "plug in new X, get predicted Y" demo? The former aligns
   with JonStats but is substantially more complex.
4. **Dataset format**: How should JSON datasets be structured? Should they
   include metadata (variable descriptions, types, ranges) or just raw data?

### Rough scope
- 3.1 (shared CSS): 1 session, mostly mechanical
- 3.2 (local datasets): ~30 minutes
- 3.3 (diagnostic plots): 1 session
- 3.4 (simulation page): 1-2 sessions depending on scope decision

---

## Tier 4: Polish

### Goal
Visual and notational consistency, minor feature additions.

### Decision points before planning
1. **KaTeX standardization**: Is it worth touching tutorials 1-2 just for
   notation consistency? They work fine with HTML entities. Only do this
   if the CSS extraction (3.1) is already touching those files.
2. **Predictor transformations**: Is this a new tutorial page, or an addition
   to existing systematic pages? Where in the flow does it fit?
3. **Convergence tolerances**: Need to balance between mathematical correctness
   (low tolerance) and animation watchability (high tolerance). Consider a
   UI toggle: "fast" vs "precise" mode.

### Rough scope
- All tasks are small (30 min - 1 hour each)
- Can be done opportunistically, no strict ordering
