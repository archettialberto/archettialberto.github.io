// BASE_URL may or may not end in '/'; normalize so `${base}foo` works.
const rawBase = import.meta.env.BASE_URL;
export const base = rawBase.endsWith('/') ? rawBase : `${rawBase}/`;

// Profile photo under public/ (square, ≥ 600px); null shows an initials placeholder.
export const PHOTO: string | null = 'img/profile.webp';

// Section ids in the header nav; labels live in i18n.ts.
export const NAV = ['about', 'news', 'publications', 'experience', 'teaching'] as const;
