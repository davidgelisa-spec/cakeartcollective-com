export const siteConfig = {
  name: 'Cake Art Collective',
  tagline: 'Artistic Cake Commissions & Classes',
  description:
    'Bespoke cake art commissions and hands-on cake decorating classes. Explore cake as a creative medium for artistic expression.',
  url: 'https://cakeartcollective.com',
  email: 'cakeartcollective@gmail.com',
  social: {
    instagram: 'https://www.instagram.com/cake_art_collective/',
    facebook: 'https://www.facebook.com/cakeartcollective/',
  },
  nav: [
    { label: 'Home', href: '/' },
    { label: 'Gallery', href: '/gallery/' },
    { label: 'Services', href: '/services/' },
    { label: 'About', href: '/about/' },
    { label: 'Tutorials', href: '/tutorials/' },
    { label: 'Weddings', href: '/gallery/weddings/' },
    { label: 'Contact', href: '/contact/' },
  ],
} as const;
