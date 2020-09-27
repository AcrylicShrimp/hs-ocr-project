module.exports = {
	sourceType: 'unambiguous',
	presets: [
		[
			'@babel/preset-env',
			{
				modules: false,
				targets: '> 0.25%, not dead',
			},
		],
	],
	plugins: [
		[
			'@babel/plugin-transform-runtime',
			{
				absoluteRuntime: false,
				corejs: 3,
				helpers: true,
				regenerator: true,
				useESModules: true,
				version: '^7.11.2',
			},
		],
	],
};
