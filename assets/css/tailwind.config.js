const themeDir = __dirname + '/../../';
// const defaultTheme = require('tailwindcss/defaultTheme')

const disabledCss = {
    'code::before': false,
    'code::after': false,
    'blockquote p:first-of-type::before': false,
    'blockquote p:last-of-type::after': false,
    pre: false,
    code: false,
    'pre code': false,
    'code::before': false,
    'code::after': false,
}

module.exports = {
    darkMode: 'class',
    // Hextra's compiled bundle already ships a (layered) base reset. This
    // local Tailwind build must NOT emit a second, unlayered Preflight: its
    // `button{margin:0;padding:0}` reset wins over Hextra's @layer utilities
    // (unlayered beats layered in the cascade) and strips the tab-button
    // styling, collapsing the tab bar to plain text.
    corePlugins: { preflight: false },
    content: [
        `${themeDir}/hugo_stats.json`,
    ],
    theme: {
        extend: {
            colors: {
                'primary-bg': '#5044E9',
                'secondary-bg': '#121212',
                'card-bg': '#F8F8F8',
                'primary-text': '#121212',
                'secondary-text': '#CACACA',
                'secondary-link': '#D4D1E9',
            },
            spacing: {
                '25': '6.25rem',
                '50': '12.5rem',
            },
            typography: {
                DEFAULT: { css: disabledCss },
                base: { css: disabledCss },
                sm: { css: disabledCss },
                lg: { css: disabledCss },
                xl: { css: disabledCss },
                '2xl': { css: disabledCss },
            },
            backgroundImage: {
                'hero-pattern': "url('/hero-pattern.svg')",
            },
            fontFamily: {
                'sans': ['Open Sans', 'ui-sans-serif', 'system-ui', 'sans-serif', '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"', '"Noto Color Emoji"'],
                'heading': ['Figtree', 'ui-sans-serif', 'system-ui', 'sans-serif', '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"', '"Noto Color Emoji"'],
            }
        },
    },
    variants: {},
    plugins: [require('@tailwindcss/typography'),]
}