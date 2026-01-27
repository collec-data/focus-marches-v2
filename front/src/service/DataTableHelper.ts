import { computed, ref, watch } from 'vue';
import { debounce } from './Debouncer';

import type { DataTablePageEvent, DataTableSortEvent } from 'primevue';

export function useApiSideDataTable(fetchData: () => void) {
    const rows = ref(10); // aka items per page
    const page = ref(0);
    const totalRecords = ref(0);
    const loading = ref(false);
    const first = computed(() => page.value * rows.value);
    const sortField = ref('nom');
    const sortOrder = ref(1);
    const search = ref('');

    function onSort(event: DataTableSortEvent) {
        sortField.value = event.sortField as string;
        sortOrder.value = event.sortOrder as number;
        page.value = 0;
    }

    watch(search, () => onFilter());

    const onFilter = debounce(() => {
        page.value = 0;
        fetchData();
    });

    function onPageChange(event: DataTablePageEvent) {
        page.value = event.page;
    }

    return {
        search,
        page,
        first,
        totalRecords,
        loading,
        rows,
        sortOrder,
        sortField,
        onSort,
        onFilter,
        onPageChange
    };
}

export const rowsPerPageOptions = [10, 25, 50];
