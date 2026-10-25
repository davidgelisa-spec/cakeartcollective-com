export const siteConfig = {
  name: 'Cake Art Collective',
  tagline: 'Artistic Cake Commissions & Classes',
  description:
    'Bespoke cake art commissions and hands-on cake decorating classes. Explore cake as a creative medium for artistic expression.',
  url: 'https://cakeartcollective.com',
  email: 'hello@cakeartcollective.com',
  social: {
    instagram: 'https://www.instagram.com/cake_art_collective/',
    facebook: 'https://www.facebook.com/cakeartcollective/',
  },
  nav: [
    { label: 'Home', href: '/' },
    { label: 'Gallery', href: '/gallery/' },
    { label: 'Weddings', href: '/gallery/weddings/' },
    { label: 'Services', href: '/services/' },
    { label: 'Classes', href: '/services/#classes' },
    { label: 'About', href: '/about/' },
    { label: 'Contact', href: '/contact/' },
  ],
  // Lower-priority links shown in the footer only
  secondaryNav: [
    { label: 'Tutorials', href: '/tutorials/' },
    { label: 'Members Area', href: '/members/' },
  ],
} as const;
