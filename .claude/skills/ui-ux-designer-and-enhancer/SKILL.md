---
name: web-design-principles
description: Battle-tested web design principles from 10+ years of professional experience. Use this skill when building web interfaces, evaluating designs, or applying practical design theory that actually drives results. Focuses on the 5 core skills that separate top 1% designers from beginners.
license: Public Domain
---

# Web Design Principles for Claude Code

## Philosophy: Design for Results, Not Just Looks

**CRITICAL INSIGHT**: Good design without good conversion practices doesn't actually help clients. I once designed a beautiful website for a client - way better than their old site, clean, modern, chef's kiss. But when we launched it, sales plummeted. Why? Because I focused on making it look pretty instead of focusing on good conversion practices.

If your design doesn't consider conversion, it's useless to your clients. This skill teaches you to build websites that are both beautiful AND effective.

---

## The Truth About User Behavior

**MYTH BUSTED**: The "F-pattern" scanning theory is outdated information that web designers keep repeating. The truth is people engage with websites in all sorts of different patterns, and forcing them to pay attention in an F-pattern might actually cause them to miss important information.

**WHAT TO DO INSTEAD**: Use Visual Hierarchy. People don't read websites - they SCAN them. Your job is to guide their eyes from most important to least important using size, contrast, position, and spacing.

---

## The Five Skills That Actually Matter

After building hundreds of websites over 10+ years, you can boil all the design knowledge needed down to just **FIVE SKILLS**. Master these, and you'll be better than 99% of designers out there:

1. **Typography** - Outside of white space, text takes up the most real estate on websites
2. **Layout** - Structure, spacing systems, and visual hierarchy  
3. **Color** - Intentional, limited palettes with purpose
4. **Code Basics** - Enough to customize and "vibe code" solutions
5. **Conversion Skills** - Design for action, not decoration

If you're trying to learn absolutely everything, take this as your permission to STOP. Focus on these five. Build around them. You'll grow way faster than chasing every single trend.

---

## SKILL 1: Typography (Top 1% Mastery)

### Why It Matters
Outside of white space, text takes up the most real estate on your website. But 99% of web designers can't tell the difference between bad type choices and good type choices. They might *feel* when something's off, but it stops there.

**Good news**: You only need to answer TWO questions to master typography for websites.

### Question 1: How Do I Pick the Right Fonts?

**The Problem**: Most web designers use the same free fonts over and over. When you use the same fonts as everyone else, your designs blend in instead of standing out.

**The Solution**: Find fonts from places that aren't overused.

**Recommended Resources**:
- **FontShare.com** - Clean, high quality, completely free
- **Uncut.wtf** - Experimental, packed with personality, tons of free fonts
- Avoid overused defaults: Inter, Roboto, Arial, Open Sans

**Font Selection Rules**:
- **Limit to 2-3 typefaces maximum** per project
- **Heading/Display fonts**: Can be decorative and personality-driven
- **Body fonts**: MUST be highly readable (consider x-height, letter spacing)
- **Pairing strategy**: Contrast serif with sans-serif, or vary weight/style within same family

### Question 2: How Do You Set Up Fonts to Improve Design?

Pro designers use a **Type Scale System** - a simple set of rules that determines font sizes, letter spacing, and line height. Once set up, typography feels intentional instead of eyeballed.

**Setting Up Your Type Scale**:

1. **Pick a base font size** for paragraph text (typically 16px)

2. **Use a scale** to make headings consistently larger
   - **Major Third Scale (1.25 ratio)** - Popular choice
   - Each level scales up by 25% from the previous
   - Example with 16px base:
     ```
     Base (paragraph): 16px
     H6: 20px (16 × 1.25)
     H5: 25px (20 × 1.25)
     H4: 31px (25 × 1.25)
     H3: 39px (31 × 1.25)
     H2: 49px (39 × 1.25)
     H1: 61px (49 × 1.25)
     ```

3. **Use REM values** - They do all the calculations for you
   ```css
   :root {
     font-size: 16px; /* base */
   }
   
   p { font-size: 1rem; }    /* 16px */
   h6 { font-size: 1.25rem; } /* 20px */
   h5 { font-size: 1.563rem; } /* 25px */
   h4 { font-size: 1.953rem; } /* 31px */
   h3 { font-size: 2.441rem; } /* 39px */
   h2 { font-size: 3.052rem; } /* 49px */
   h1 { font-size: 3.815rem; } /* 61px */
   ```

**Letter Spacing**:
- **Body text**: Don't touch it. Keep default for readability.
- **Headings**: Tighten it up slightly. As text gets larger, it looks cleaner with reduced spacing.
  ```css
  h1, h2, h3 {
    letter-spacing: -0.02em;
  }
  ```

**Line Height**:
- **Paragraphs**: 150% of font size (multiply by 1.5)
  - If font is 16px, line-height is 24px (16 × 1.5)
  - Gives text room to breathe, easier to read
  ```css
  p {
    line-height: 1.5; /* 150% */
  }
  ```
- **Headings**: Tighten up as they get bigger for impact
  ```css
  h1, h2, h3 {
    line-height: 1.2; /* 120% */
  }
  ```

**Shortcut**: Use **TypeScale.net**
- Pick your base size
- Choose a ratio
- Generates the whole system in 2 minutes
- Makes your typography look pro instantly

### Typography Elements for Websites

**Three main text elements to consider**:

1. **H1 (Main Headers)** 
   - Biggest, most prominent text on the page
   - Describes what the entire page is about
   - Should be unmissable

2. **H2 (Subheadings)**
   - Divvy up the rest of the page
   - Guide user's attention through sections
   - Create scannable structure

3. **P (Paragraph Text)**
   - Don't use decorative fonts here
   - Might look cool, but kills readability
   - Prioritize legibility over style

### Readability Rules
- Never pure black (#000) on pure white (#fff) - causes eye strain
- Use dark gray on off-white (#1a1a1a on #fafafa)
- Line length: 45-75 characters per line (optimal: 66 characters)
- Avoid centered body text - only for headlines/short content

---

## SKILL 2: Layout (Structure & Systems)

### Why It Matters
Most new designers drag things around until it "feels right." Pro designers don't guess - they have systems that guarantee results every time.

You don't need to memorize tons of layout rules. You just need **THREE THINGS**:
1. A **grid system** for structure
2. A **spacing system** for rhythm
3. **Visual hierarchy** to guide the eye

### Grid System

**The Foundation**: Think of this as your layout's skeleton.

**Recommended Setup**:
- **Desktop**: 12 columns
- **Tablet**: 8 columns  
- **Mobile**: 4 columns

**Why 12 columns?**
- Super flexible to divide evenly
- Can be 2 columns (6+6), 3 columns (4+4+4), 4 columns (3+3+3+3), etc.
- Easy to work with for any layout

**Figma Setup**:
1. Select your frame
2. Go to Layout Grid
3. Click + to add guide
4. Change Grid → Columns
5. Set column count (12 for desktop)

### Spacing System: 8-Point Grid

**What It Is**: All spacing uses multiples of 8 (8, 16, 24, 32, 40, 48, 56, 64...)

**Why It Works**:
- Creates consistent rhythm
- Gives design room to breathe
- Same approach used by Google (Material Design) and Apple
- If major players like Google and Apple use it, you can't ignore it

**Implementation**:
```css
:root {
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 24px;
  --spacing-lg: 32px;
  --spacing-xl: 48px;
  --spacing-2xl: 64px;
  --spacing-3xl: 96px;
}
```

**Spacing Guidelines**:
- **Within components**: 8px, 12px, 16px
- **Between related components**: 24px, 32px
- **Between sections**: 48px, 64px, 96px

**Figma Setup**:
1. Same as columns setup
2. Add layout guide
3. Keep on "Grid" (don't change to columns)
4. Change grid size to 8

### Visual Hierarchy: Guide the Eye

**The Truth**: People don't read websites. They SCAN them. Your layout needs to guide eyes from most important to least important.

**Four Principles to Master**:

1. **Proximity** - Keep related things close together
   - Related content groups together visually
   - Unrelated content separates with significant space
   - Create clear visual relationships

2. **Size** - Signals importance
   - Larger = more important
   - Smaller = less important
   - Big headings + big images draw attention first
   - Use dramatic size contrast (not subtle differences)

3. **Contrast** - Creates visual interest
   - **Size contrast**: Large vs small elements
   - **Weight contrast**: Bold vs light typography
   - **Color contrast**: Saturated vs muted
   - **Opacity contrast**: 100% headers vs 70% body text signals reading priority

4. **Alignment** - Clean lines = clear structure
   - Everything aligns to something
   - Create invisible grids with alignment
   - Consistent edges throughout design
   - No random placement

**When you use these four together**: You build layouts that feel effortless to navigate. That's what separates pros from beginners.

### Layout Best Practices

**Navigation**: 5-7 items maximum
- More than 7 = cognitive overload
- Descriptive, clear labels
- Show active/current page clearly

**Content Scannability**:
- Short paragraphs (3-4 sentences max)
- Subheadings every 300 words
- Bullet points for lists
- Bold key phrases sparingly

**White Space**:
- Not wasted space - it's a design element
- Increases comprehension by up to 20%
- Makes content feel premium
- Don't fear empty space

---

## SKILL 3: Color (Intentional & Purposeful)

### Why It Matters
For many designers, color feels overwhelming. There are millions of colors - how do you know what works?

**The Secret**: Pro designers don't use MORE color. They use color MORE INTENTIONALLY.

### The 60-30-10 Rule

The most popular system for visual balance. Each color has a specific JOB.

**Breakdown**:
- **60% Neutral/Dominant Colors** (Grays, Blacks, Whites)
  - Background colors
  - Body text
  - Creates foundation
  
- **30% Secondary Colors** (Brand colors)
  - Backgrounds for cards
  - Headers
  - Visuals
  - Supporting elements
  
- **10% Accent Colors** (High contrast)
  - Buttons
  - CTAs
  - Elements that MUST stand out
  - Drive action

**Example Palette**:
```css
:root {
  /* 60% - Neutrals */
  --color-bg: #fafafa;
  --color-text: #1a1a1a;
  --color-gray: #6b7280;
  
  /* 30% - Secondary/Brand */
  --color-primary: #2563eb;
  --color-primary-light: #60a5fa;
  
  /* 10% - Accent */
  --color-accent: #f59e0b;
  --color-cta: #dc2626;
}
```

### Limit Your Color Palette

**Rule**: 2-3 different colors maximum for any project

**Why**: One good color used well beats five random colors every day.

**As you get more confident**: You can expand palettes, but don't feel like you need to.

### Use Opacity Instead of More Colors

**Pro Tip**: Take your primary color and adjust opacity to create variations instead of adding new colors.

**Example**:
```css
.primary-100 { color: rgba(37, 99, 235, 1); }    /* 100% opacity */
.primary-80  { color: rgba(37, 99, 235, 0.8); }  /* 80% opacity */
.primary-60  { color: rgba(37, 99, 235, 0.6); }  /* 60% opacity */
.primary-40  { color: rgba(37, 99, 235, 0.4); }  /* 40% opacity */
.primary-20  { color: rgba(37, 99, 235, 0.2); }  /* 20% opacity */
```

**Learned from**: Google's Material Design - they use opacity to create color variations throughout their system.

### Prioritize Contrast (Accessibility)

**CRITICAL**: Your color combo might look nice, but if users can't read it, it doesn't matter how pretty it is.

**WCAG Standards**:
- **Large text** (18pt+ or 14pt+ bold): 3:1 minimum contrast
- **Small text**: 4.5:1 minimum contrast
- **Interactive elements**: 3:1 against adjacent colors

**Check Contrast in Figma**:
1. Select text
2. Go to Fill
3. Click contrast icon (top right corner)
4. Tells you pass/fail instantly

**Recommended Tool**: **Coolers.co**
- Input all brand colors
- Click "Color Contrast Checker"
- Instantly shows which combinations pass/fail
- Super helpful for accessibility compliance

### Color Psychology

Use color strategically based on psychology:
- **Red**: Urgency, passion, danger (CTAs, errors, sales)
- **Blue**: Trust, professionalism (corporate, finance, tech)
- **Green**: Success, growth, health (confirmations, eco)
- **Yellow**: Warning, attention, optimism
- **Orange**: Friendly, enthusiastic (CTAs, playful brands)
- **Purple**: Luxury, creativity (premium brands)

### Don't Build Palettes from Scratch

**Pro Tip**: Most great palettes weren't made from thin air. They were borrowed and refined.

**Use CSS Overview Tool**:
1. Open any website
2. Open Chrome DevTools
3. Click three dots (top right)
4. More Tools → CSS Overview
5. Capture Overview
6. Get ALL colors, fonts, type scale from that site

Great for inspiration and learning from sites you admire.

---

## SKILL 4: Code Basics (Just Enough to Customize)

### Why It Matters
You don't need to be a full-stack developer. You just need to know the basics and know how to use the right tools to get the rest of the way.

If you want to be better than 99% of designers, get comfortable with code. But you don't need to know how to build a full web app.

### The Essentials

**What to Learn**:
1. **HTML** - Structure of content
2. **CSS** - Styling and layout
3. **JavaScript** - Interaction and behavior
4. **PHP Basics** (if using WordPress) - Can go a long way

**That alone takes you further than most web designers would ever go.**

### The 80/20 Strategy: "Vibe Coding"

**The Real Trick**: Find solutions that are 80% of the way there, then "vibe code" the rest.

**What This Means**:
1. Find code snippets/templates close to what you need
2. Use CodePen, ChatGPT, or snippet libraries
3. Get something that's 80% there
4. Tweak and customize the remaining 20%

**Real Example**: A friend (not a developer) customized a WordPress WooCommerce plugin to have a custom checkout process for his wife's website. He didn't need to be a full-stack developer - he just learned by doing.

### Learning Resources

**Start Here**:
- **Code Academy** - Free courses for HTML, CSS, JavaScript
- **Learn by doing** - Build actual projects, solve real problems
- **Don't overthink it** - Use the tools available to you

### Modern Tools to Leverage

**AI-Assisted Coding**:
- ChatGPT for code generation
- GitHub Copilot
- Claude (for code explanations and debugging)

**Code Snippet Libraries**:
- CodePen
- CSS-Tricks
- GitHub repositories

**Frameworks** (when ready):
- Tailwind CSS - Utility-first CSS
- Bootstrap - Component library
- React - JavaScript library

**The Goal**: You don't need to memorize everything. You need to know enough to find solutions and customize them.

---

## SKILL 5: Conversion Skills (Design for Action)

### Why It Matters Most

**HARSH TRUTH**: Most designers design for looks. Pro designers design for ACTION.

Early in my career, I redesigned a client's website from the ground up. It looked amazing - way better than the original. But after launch, their sales plummeted.

**Why?** I focused so much on design that I ignored the user journey. That was a turning point and a really hard lesson to learn.

### What Is Good Conversion Design?

**Core Principle**: Reduce friction for users. Make it stupid easy for users to:
- Find what they're looking for
- Buy a product
- Sign up for a service
- Take the desired action

**How?** Through **Clarity**, **Scannability**, and **Motivation**.

### 1. Clarity: Crystal Clear Purpose

**Be clear about**:
- Who the company/person is
- What the user is supposed to do next
- Why they should even care

**Implementation**:
- **Hero section**: Clear value proposition in first 5 seconds
- **Headline**: Benefit-focused, not feature-focused
  - ❌ "Advanced AI-powered analytics platform"
  - ✅ "Make better decisions with data that makes sense"
- **Navigation**: Simple, obvious, maximum 5-7 items

### 2. Scannability: Design for Scanning

**Remember**: People aren't reading websites - they're scanning.

**Make It Scannable**:
- **Short paragraphs**: 3-4 sentences maximum
- **Subheadings**: Every 200-300 words
- **Bullet points**: For lists and key information
- **Bold key phrases**: Sparingly, only the most important words
- **Visual breaks**: Images, whitespace, cards

**Layout Strategy**: Set things out so people can bounce around and make decisions quickly.

### 3. Motivation: Speak to Feelings

**It's not enough to be pretty.** You need to speak to the heart of the user. Speak to the thing that's driving them to say yes or no.

**Elements That Build Trust**:
- **Social Proof**: Testimonials, reviews, case studies
- **Trust Signals**: Badges, certifications, security icons
- **Real Photos**: Actual people/products, not stock photos
- **Specifics**: "Join 10,247 designers" vs "Join thousands"

**People buy from brands they know, like, trust, and FEEL something from.**

### Every Page Needs ONE Goal

**Critical Rule**: Each page should have just ONE goal. That's it.

**Examples of Single Goals**:
- Buy a product
- Sign up for a phone call
- Download a lead magnet
- Subscribe to newsletter
- Create an account

**You lose users when trying to do too much at once.**

### Strategic CTAs (Call-to-Actions)

**Placement Rules**:
- **Visible within seconds** of landing on page
- **Hero section**: Clear primary CTA
- **Navigation**: CTA button in nav bar
- **Every 2-3 scroll sections**: Repeat the CTA
- **Before footer**: Final chance to convert

**CTA Best Practices**:
- **High contrast**: Must stand out from everything
- **Action-oriented text**: 
  - ✅ "Start Free Trial"
  - ✅ "Get Your Free Guide"
  - ❌ "Submit" 
  - ❌ "Click Here"
- **Solid buttons**: No ghost buttons (outline only)
- **Generous size**: Easy to click, especially on mobile (min 48px height)

### Design for the RIGHT Audience

**Critical Mindset Shift**: It doesn't matter if YOU love the design. It doesn't even matter if your CLIENT loves the design.

**Who does it matter for?** The website VISITORS.

**Action Items**:
1. **Do research**: Who's actually using this website?
2. **Choose fonts based on audience**: Not personal preference
3. **Choose colors based on audience**: Not what you like
4. **Choose layout based on audience**: Not client opinion

**Examples**:
- **Tech startup**: Modern, clean, minimal
- **Luxury brand**: Elegant, sophisticated, spacious
- **Kids' product**: Playful, colorful, fun
- **Law firm**: Professional, trustworthy, traditional

The design must match the audience's expectations and preferences.

### Conversion Optimization Checklist

Before launching:
- [ ] One clear goal per page
- [ ] CTA visible within 3 seconds
- [ ] CTA repeated every 2-3 scroll sections
- [ ] Headlines focus on benefits, not features
- [ ] Social proof included (testimonials, reviews)
- [ ] Trust signals visible (security badges, certifications)
- [ ] Forms are simple (only ask what's necessary)
- [ ] Mobile CTAs are easily tappable (min 48px)
- [ ] Page loads fast (under 3 seconds)
- [ ] Value proposition is crystal clear

---

## Additional Essential Principles

### Responsive Design

**Mobile-First Approach**:
1. Design for smallest screen first
2. Progressively enhance for larger screens
3. Touch targets minimum 48x48px
4. Test on real devices

**Breakpoints**:
```css
/* Mobile: base styles 320px+ */

@media (min-width: 640px) { /* Tablets */ }
@media (min-width: 1024px) { /* Laptops */ }
@media (min-width: 1280px) { /* Desktops */ }
```

### Accessibility

**Non-Negotiable Requirements**:
- Keyboard navigation works everywhere
- Alt text on all images
- ARIA labels where needed
- Color contrast meets WCAG AA (4.5:1 minimum)
- Forms have proper labels
- Focus states visible on interactive elements

**Testing Tools**:
- Browser DevTools Accessibility Panel
- WAVE extension
- Lighthouse audit

### Performance

**Performance Budget**:
- First Contentful Paint < 1.8s
- Largest Contentful Paint < 2.5s
- Total Blocking Time < 300ms

**Quick Wins**:
- Optimize images (WebP format)
- Lazy load images below fold
- Minimize JavaScript
- Use CSS for animations (not JS)
- Load critical CSS inline

---

## Common Mistakes to Avoid

Based on 10+ years of real projects:

1. **Ghost Buttons** - People don't see or click them
2. **Too Many Fonts** - Stick to 2-3 maximum
3. **Poor Contrast** - Always check accessibility
4. **No Clear CTA** - Make the action obvious
5. **Designing for Yourself** - Design for the audience
6. **Too Many Options** - Limit choices, reduce friction
7. **Ignoring Mobile** - Most traffic is mobile
8. **Auto-Playing Media** - Annoys users, hurts accessibility
9. **Slow Loading** - Users bounce in 3 seconds
10. **Pretty but Useless** - Design must drive results

---

## The Continuous Learning Mindset

**Critical Truth**: Web designers don't age like fine wine. We age like a loaf of bread left on the counter. We go stale unless we keep learning.

**Why This Matters**:
- Web design industry changes FAST
- What worked 5 years ago might not work today
- What works today might not work in 5 years
- If you don't challenge yourself and stay updated, you fall behind

**Will AI Take Our Jobs?**
- Probably not all of them
- But will AI take LAZY web designer jobs? Absolutely.
- The only way to stay valuable: Keep learning, keep adjusting, keep leveling up

**How to Keep Learning**:
1. Build real projects constantly
2. Study websites you admire (use CSS Overview tool)
3. Follow design trends but don't blindly copy
4. Learn from failures (like my sales-plummeting website)
5. Get feedback from actual users
6. Stay curious about new tools and techniques

---

## Tools & Resources

### Typography
- **TypeScale.net** - Generate type scale systems instantly
- **FontShare.com** - Free, high-quality fonts
- **Uncut.wtf** - Experimental, personality-driven fonts

### Color
- **Coolers.co** - Color palette generator + contrast checker
- **CSS Overview** (Chrome DevTools) - Extract colors from any site

### Layout
- **Figma** - Design tool with built-in grid systems
- Tailwind CSS - Utility-first CSS with 8-point grid built-in

### Code Learning
- **Code Academy** - Free courses for HTML, CSS, JavaScript
- **CodePen** - Find and fork code snippets
- **ChatGPT/Claude** - AI assistance for code generation

### Performance & Accessibility
- **Lighthouse** (Chrome DevTools) - Performance audit
- **WAVE** - Accessibility checker
- **WebPageTest** - Performance testing

---

## Final Checklist

Before launching ANY web project:

**Typography**:
- [ ] Using 2-3 fonts maximum
- [ ] Type scale system implemented
- [ ] Line height 1.5 for paragraphs, 1.2 for headings
- [ ] Font sizes scale consistently

**Layout**:
- [ ] Grid system in place (12 columns desktop)
- [ ] 8-point spacing system used throughout
- [ ] Visual hierarchy clear (size, proximity, contrast, alignment)
- [ ] White space generous and intentional

**Color**:
- [ ] 60-30-10 rule followed
- [ ] 2-3 colors maximum
- [ ] Contrast ratios meet WCAG (4.5:1 minimum)
- [ ] Colors checked with Coolers.co

**Conversion**:
- [ ] One clear goal per page
- [ ] CTA visible within 3 seconds
- [ ] CTAs repeated every 2-3 scroll sections
- [ ] Designed for target audience (not yourself)
- [ ] Social proof included
- [ ] Forms simple and minimal

**Technical**:
- [ ] Responsive on mobile, tablet, desktop
- [ ] Performance under 3 seconds
- [ ] Keyboard navigation works
- [ ] All images have alt text
- [ ] Focus states visible

---

## Remember

**Good design is invisible.** Users shouldn't notice your design choices - they should simply enjoy using your website AND take the desired action.

**Design for results, not just aesthetics.**

**Master the five skills:**
1. Typography
2. Layout  
3. Color
4. Code Basics
5. Conversion

**And if you don't quit, you win.**