# Template Refactoring TODO

## Task: Refactor Flask templates to use single base template

### Step 1: Update base.html with proper navbar
- [x] templates/base.html - Add flexbox navbar with Coding Practice, Profile (right), Logout (right)

### Step 2: Update templates to extend base.html

#### Category Pages (have navbar + container structure)
- [x] templates/home.html - Convert to extend base.html
- [x] templates/aptitude.html - Convert to extend base.html
- [x] templates/aptitude_simple.html - Convert to extend base.html
- [x] templates/coding.html - Convert to extend base.html
- [x] templates/codings.html - Convert to extend base.html
- [x] templates/technical.html - Convert to extend base.html
- [x] templates/mock.html - Convert to extend base.html
- [x] templates/index.html - Convert to extend base.html

#### User Pages
- [x] templates/profile.html - Convert to extend base.html
- [x] templates/leaderboard.html - Convert to extend base.html
- [x] templates/results.html - Convert to extend base.html

#### Quiz Pages
- [x] templates/levels.html - Convert to extend base.html
- [x] templates/quiz.html - Convert to extend base.html

### Step 3: Skip these files (special cases)
- [x] templates/LOGIN.HTML - Kept as-is (auth page)
- [x] templates/register.html - Kept as-is (auth page)
- [x] templates/code_practice.html - Kept as-is (special layout)
- [x] templates/apptitude.html - Just a content fragment

### Verification
- [x] Verify no duplicate navbar exists (only code_practice.html has its own navbar - intentional)
- [x] Verify all pages inherit from base.html (13 templates updated)
