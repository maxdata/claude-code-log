export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set([]),
	mimeTypes: {},
	_: {
		client: {start:"_app/immutable/entry/start._XL06-ug.js",app:"_app/immutable/entry/app.Cku99LXr.js",imports:["_app/immutable/entry/start._XL06-ug.js","_app/immutable/chunks/DjIrHA-b.js","_app/immutable/chunks/59xXa_gx.js","_app/immutable/chunks/DddK18v8.js","_app/immutable/entry/app.Cku99LXr.js","_app/immutable/chunks/DddK18v8.js","_app/immutable/chunks/59xXa_gx.js","_app/immutable/chunks/Bzak7iHL.js","_app/immutable/chunks/DBwkRAqr.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js'))
		],
		remotes: {
			
		},
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {
			
			return {  };
		},
		server_assets: {}
	}
}
})();
