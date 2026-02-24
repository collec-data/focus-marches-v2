export async function mockRouter(params: any): Promise<void> {
    const VueRouter = await import('vue-router');
    VueRouter.useRoute.mockReturnValue({
        params: params,
        path: '/lorem/ipsum/dolor',
        query: {}
    });
}
