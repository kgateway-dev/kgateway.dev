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
                'ubuntu': ['Ubuntu', 'ui-sans-serif', 'system-ui', 'sans-serif', '"Apple Color Emoji"', '"Segoe UI Emoji"', '"Segoe UI Symbol"', '"Noto Color Emoji"'],
            }
        },
    },
    variants: {},
    plugins: [require('@tailwindcss/typography'),]
}