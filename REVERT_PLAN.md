# REVERT PLAN - Remove All UI Changes

## Objective
Revert all UI design changes back to the original simple design.

## Files to Revert

### 1. static/style.css
- Replace with simple, basic CSS (no gradients, no glassmorphism)
- Keep only essential styling

### 2. Templates to Update (Remove base.html inheritance)
- templates/index.html - Remove extends base.html, use standalone simple template
- templates/home.html - Remove extends base.html  
- templates/aptitude.html - Remove extends base.html
- templates/aptitude_simple.html - Remove extends base.html
- templates/coding.html - Remove extends base.html
- templates/codings.html - Remove extends base.html
- templates/technical.html - Remove extends base.html
- templates/mock.html - Remove extends base.html
- templates/profile.html - Remove extends base.html
- templates/leaderboard.html - Remove extends base.html
- templates/results.html - Remove extends base.html
- templates/levels.html - Remove extends base.html
- templates/quiz.html - Remove extends base.html

### 3. Delete base.html (no longer needed)
- templates/base.html

### 4. Keep as-is (already simple)
- templates/LOGIN.HTML - Already simple
- templates/register.html - Already simple
- templates/code_practice.html - Already simple

## Simple Design Requirements
- Plain white backgrounds
- Simple blue/gray color scheme
- Basic form inputs
- Simple navbar (no flexbox)
- No animations
- No glassmorphism
- No gradients
- Basic card styling

## Approach
1. Create simple style.css with basic styling
2. Convert each template to standalone HTML (remove base.html extends)
3. Add basic navbar to each template
4. Delete base.html
