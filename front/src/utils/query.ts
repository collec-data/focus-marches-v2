import type { Options } from '@/client';
import type { RequestResult, TDataShape } from '@/client/client/types.gen';
import type { Ref, WatchSource } from 'vue';
import { onWatcherCleanup, ref, watch } from 'vue';

type ReactiveFetchResultInitial = {
    status: 'pending';
    asyncStatus: 'idle';
    data: null;
    error: null;
};

type ReactiveFetchResultLoading<DATA, ERROR> = {
    status: 'success' | 'error' | 'pending';
    asyncStatus: 'loading';
    data: DATA | null;
    error: ERROR | null;
};
type ReactiveFetchResultSuccess<DATA> = {
    status: 'success';
    asyncStatus: 'idle';
    data: DATA;
    error: null;
};
type ReactiveFetchResultError<ERROR> = {
    status: 'error';
    asyncStatus: 'idle';
    data: null;
    error: ERROR;
};

type ReactiveFetchResult<DATA, ERROR> = ReactiveFetchResultInitial | ReactiveFetchResultLoading<DATA, ERROR> | ReactiveFetchResultSuccess<DATA> | ReactiveFetchResultError<ERROR>;

export const useReactiveFetch = <F extends (options: O) => R, O extends Options<TDataShape, false>, R extends RequestResult<R, E, false, 'fields'>, E>(fetchFunc: F, optionsRef: WatchSource<O>): Ref<ReactiveFetchResult<Awaited<R>['data'], any>> => {
    let controller: AbortController | null = null;

    const state = ref<ReactiveFetchResult<Awaited<R>, any>>({
        status: 'pending',
        asyncStatus: 'idle',
        data: null,
        error: null
    });

    watch(
        optionsRef,
        (opts) => {
            controller?.abort();
            controller = new AbortController();
            const { signal } = controller;
            signal.onabort = () => {
                console.log('aborted');
            };

            state.value = { ...state.value, asyncStatus: 'loading' };

            fetchFunc({
                ...opts,
                fetch: (input, init) => fetch(input, { ...init, signal })
            }).then(
                (result) => {
                    state.value = {
                        ...state.value,
                        asyncStatus: 'idle',
                        status: 'success',
                        data: result,
                        error: null
                    };
                },
                (error) => {
                    state.value = {
                        ...state.value,
                        asyncStatus: 'idle',
                        status: 'error',
                        data: null,
                        error: error
                    };
                }
            );

            // On nettoie en sortant (permet d'annuler les requêtes en cours qui ont été initiées par un composants à sa destruction).
            onWatcherCleanup(() => {
                controller?.abort();
            });
        },
        {
            immediate: true
        }
    );

    return state;
};
