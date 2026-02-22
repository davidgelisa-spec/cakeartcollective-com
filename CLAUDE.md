# CLAUDE.md — Cake Art Collective

## Business Overview
Cake Art Collective is a custom cake business run by Lisa. The business offers:
- **Custom celebration cakes** — bespoke cakes for weddings, birthdays, and special occasions
- **Cake decorating classes** — both in-person and online
- **Online tutorials** — coming soon (pre-launch placeholder page on the site)

Website: cakeartcollective.com

## Tech Stack
- **Astro 5** — static site generator
- **Tailwind CSS 4** — via `@tailwindcss/vite` plugin (NOT the older `@astrojs/tailwind`)
- **TypeScript** — strict mode
- **Sharp** — image optimisation (dev dependency)
- **@astrojs/sitemap** — XML sitemap generation

## Project Structure

src/
    assets/images/              # Cake photos, hero images (optimised via astro:assets)
    components/
        layout/
            Header.astro        # Site navigation with logo
            Footer.astro        # Footer with contact info and social links
        sections/
            Hero.astro           # Homepage hero banner
            FeaturedWork.astro   # Gallery preview on homepage
            ServicesOverview.astro # Services summary on homepage
            ClassesTeaser.astro  # Classes mention on homepage
            About.astro          # About section content
        ui/
            Button.astro         # Reusable button component
            Card.astro           # Reusable card (for gallery, services)
            SectionHeading.astro # Consistent section headings
        SEO.astro               # Meta tags, OG tags, canonical URLs
    data/
        siteConfig.ts           # Centralised site config (business info, nav, contact)
    layouts/
        BaseLayout.astro        # HTML shell, font preloading, global styles
    pages/
        index.astro             # Homepage
        gallery/index.astro     # Gallery / Portfolio
        about/index.astro       # About Lisa
        services/index.astro    # Services & Pricing
        contact/index.astro     # Contact page
        tutorials/index.astro   # Coming Soon placeholder
    styles/
        global.css              # Tailwind directives + CSS custom properties
public/
    robots.txt
    favicon.svg

## Design System

### Design Direction — Artist's Portfolio
Inspired by fine artist websites (e.g. Amy T. Won). The site should feel like an artist's portfolio, not a traditional cake/wedding vendor. Confident, curated, unhurried. Let the photography dominate.

### Colour Palette — Teal, Gold & Cream
| Role             | Colour           | Hex       |
|------------------|------------------|----------|
| Primary          | Deep Teal        | #4F8E96   |
| Primary Dark     | Dark Teal        | #3A6E75   |
| Primary Light    | Soft Teal        | #7AACB2   |
| Secondary        | Burnished Gold   | #B49A4E   |
| Secondary Light  | Pale Gold        | #D4C88A   |
| Background       | Warm Cream       | #F7F5EE   |
| Background Alt   | Deeper Cream     | #F0EDE5   |
| Text Primary     | Near Black       | #1C1C1A   |
| Text Secondary   | Warm Grey        | #6B6862   |
| White            | White            | #FFFFFF   |
| Border           | Subtle Warm Grey | #D8D4CA   |

**No orangey colours.** Gold should read as gold, not amber/orange.

### Typography
- **Headings:** Bodoni Moda (serif) — high-contrast, editorial, confident
- **Body text:** Inter (sans-serif) — clean, modern, highly readable
- **Font loading:** Google Fonts in BaseLayout.astro
- **Headings are NOT uppercase** — natural case, let the typeface speak
- **h1:** Italic, weight 400, subtle letter-spacing
- **h2/h3:** Weight 400, minimal letter-spacing

### Overall Feel
- Artist's portfolio — confident, curated, gallery-like
- Cake presented as art, not product
- Generous whitespace — let images breathe
- Minimal decoration — no gold rules, no card borders, no shadows
- Photography dominates; design stays quiet
- Asymmetric layouts where appropriate (hero, about sections)
- Warm earthy cream background, never stark white

### Components Style Guide
- **Links/CTAs:** Text-based with bottom border, uppercase 11px tracking-[0.2em], hover transitions to teal. No filled buttons.
- **Gallery items:** No borders, no cards — images float directly on the page with subtle opacity hover
- **Section headings:** Bodoni Moda, natural case, no decorative underlines
- **Forms:** Underline-only inputs (border-bottom), transparent background, minimal
- **Navigation:** Minimal header, cream background with blur, no border-bottom. Nav links are small uppercase.
- **Footer:** Light, text-only, border-top separator, no dark background block

## Image Handling
- Store all images in `src/assets/images/`
- Import using `import` statements and use with Astro's `<Image>` component
- Astro will auto-optimise to WebP format
- Always include descriptive `alt` text for accessibility and SEO
- Use `loading="lazy"` for below-the-fold images
- Hero images: aim for 1920px wide originals
- Gallery images: aim for 1200px wide originals
- Keep original high-quality files — Astro handles compression

## Configuration

### astro.config.mjs
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://cakeartcollective.com',
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [sitemap()],
  trailingSlash: 'always',
});

### global.css
See `src/styles/global.css` for the current Tailwind `@theme` block with all colour and font tokens.

## Page Descriptions

### Homepage (index.astro)
- Hero section with a stunning cake photo and tagline
- Brief intro to Cake Art Collective
- Featured work preview (3–4 best cake images linking to gallery)
- Services overview (custom cakes + classes at a glance)
- Classes teaser mentioning in-person and online options
- Call to action (contact / get a quote)

### Gallery (gallery/index.astro)
- Grid layout showcasing cake photos
- Categories: Wedding, Birthday, Celebration, Novelty
- Each image opens larger or links to detail

### About (about/index.astro)
- Lisa's story and passion for cake art
- Solo business — personal, warm, authentic tone
- Photo of Lisa (if available) or workspace

### Services & Pricing (services/index.astro)
- Custom cakes: what's included, starting prices, how to order
- Classes: in-person and online options, what students learn
- Clear call-to-action to get in touch

### Contact (contact/index.astro)
- Contact form or email/phone details
- Location info (if relevant for in-person classes)
- Social media links

### Tutorials — Coming Soon (tutorials/index.astro)
- Elegant placeholder with "Coming Soon" messaging
- Brief description of what tutorials will offer
- Option to collect email for notifications

## Key Patterns
- All pages use `BaseLayout.astro` as the layout wrapper
- Navigation and footer are consistent across all pages
- Use `siteConfig.ts` for any repeated data (business name, phone, email, nav links)
- File-based routing with trailing slashes (e.g., `/gallery/` not `/gallery`)
- SEO component included on every page with unique title and description

## Build & Deploy
- **Dev server:** `npm run dev` → http://localhost:4321
- **Build:** `npm run build` → outputs to `dist/`
- **Deploy:** Push to GitHub → Cloudflare Pages auto-deploys
- **Live URL (temporary):** cakeartcollective-com.pages.dev
- **Live URL (final):** cakeartcollective.com

## Common Tasks

### Adding a new page
1. Create `src/pages/pagename/index.astro`
2. Import and use `BaseLayout.astro`
3. Add the page to the nav array in `siteConfig.ts`
4. Include the `SEO` component with a unique title and description

### Adding new cake photos to the gallery
1. Drop the image into `src/assets/images/`
2. Import it in the gallery page or component
3. Use Astro's `<Image>` component with a descriptive `alt` tag

### Updating colours or fonts
1. Edit CSS variables in `src/styles/global.css`
2. Update the design system section in this CLAUDE.md to match