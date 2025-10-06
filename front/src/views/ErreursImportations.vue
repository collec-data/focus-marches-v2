<script setup lang="ts">
import { getErreursImportErreursImportGet } from '@/client';
import { onMounted, ref } from 'vue';

import type { DecpMalFormeDto } from '@/client';
const listDecpMalFormes = ref<Array<DecpMalFormeDto>>([]);

onMounted(() => {
    getErreursImportErreursImportGet({ query: { limit: 50 } }).then((response) => {
        if (response.data) {
            listDecpMalFormes.value = response.data;
        }
    });
});
</script>

<template>
    <section className="card">
        <h2>Erreurs lors de l'importation</h2>
        <div>
            <Panel v-for="decp in listDecpMalFormes" :key="decp.uid">
                <ul>
                    <li v-for="erreur in decp.erreurs" :key="erreur.uid">
                        <Message severity="error"> [{{ erreur.type }}] {{ erreur.message }} - {{ erreur.localisation }} </Message>
                    </li>
                </ul>
                <pre>
                        <code>
                            {{ decp.decp }}
                        </code>
                    </pre>
            </Panel>
        </div>
    </section>
</template>
