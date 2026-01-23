// from https://dev.to/jacobandrewsky/implementing-debouncing-in-vue-22jb

export function debounce(fn) {
    let timer;
    return function (...args) {
        if (timer) {
            clearTimeout(timer); // clear any pre-existing timer
        }
        // @ts-expect-error typing too strict there
        // eslint-disable-next-line @typescript-eslint/no-this-alias
        const context = this;
        timer = setTimeout(() => {
            fn.apply(context, args); // call the function if time expires
        }, 300);
    };
}
