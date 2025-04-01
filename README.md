# README.md
AI HTML & CSS Restructuring Guidelines
Real-World Design Consideration

Before restructuring, reason out how a real-world HTML & CSS template would be structured for readability, accessibility, and responsiveness.
Ensure proper HTML semantics and class structuring for maintainability.
Preserve Jinja Variables & Syntax

DO NOT modify or override Jinja variables ({{ variable }} or {% %} blocks). They must remain exactly as they are to prevent breaking backend functionality.
Respect External JavaScript Compatibility

Do not change element ids, class names, data-attributes, or structural references that external JavaScript depends on.
The restructuring should be CSS & HTML-only unless explicitly instructed otherwise.
Styling & Layout Adjustments

Apply a clean, structured, and real-world CSS approach while keeping flexibility for future modifications.
You may rearrange HTML elements for better structure and user experience, but do not rename or remove essential elements.
Use a consistent class naming convention that follows best practices.
Maintain Logical Grouping

Related elements (e.g., product info, images, cart controls) should be grouped logically within appropriate containers (div, section, article, etc.).
Ensure the design remains mobile-responsive by default.
Emphasize Clarity & Readability

Keep the code clean and well-indented for easier debugging and modifications.
Use aria-labels or proper text associations where relevant for accessibility.
Additional Rule:
🔴 DO NOT modify or remove any Jinja variable, route, or existing backend logic references. The only allowed modifications are restructuring and styling the HTML & CSS.