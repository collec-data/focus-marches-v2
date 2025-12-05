export async function mockRouter(params): Promise<void> {
    const VueRouter = await import('vue-router');
    VueRouter.useRoute.mockReturnValue({
        params: params,
        path: '/lorem/ipsum/dolor',
        query: {}
    });
}
