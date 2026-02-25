import { computed, reactive, ref } from 'vue';

export interface layoutConfigInterface {
    preset: string;
    primary: string;
    surface: null | string;
    darkTheme: boolean;
}

const layoutConfig = reactive<layoutConfigInterface>({
    preset: 'Aura',
    primary: 'emerald',
    surface: null,
    darkTheme: false
});

const menuMobileActive = ref(false);

export function useLayout() {
    const toggleDarkMode = () => {
        if (!document.startViewTransition) {
            executeDarkModeToggle();

            return;
        }

        document.startViewTransition(() => executeDarkModeToggle());
    };

    const executeDarkModeToggle = () => {
        layoutConfig.darkTheme = !layoutConfig.darkTheme;
        document.documentElement.classList.toggle('app-dark');
    };

    const toggleMenu = () => {
        menuMobileActive.value = !menuMobileActive.value;
    };

    const isSidebarActive = computed(() => menuMobileActive.value);

    const isDarkTheme = computed(() => layoutConfig.darkTheme);

    const getPrimary = computed(() => layoutConfig.primary);

    const getSurface = computed(() => layoutConfig.surface);

    return {
        layoutConfig,
        menuMobileActive,
        toggleMenu,
        isSidebarActive,
        isDarkTheme,
        getPrimary,
        getSurface,
        toggleDarkMode
    };
}
