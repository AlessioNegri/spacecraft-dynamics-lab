import * as path from 'node:path'
import * as vite from 'electron-vite'

import react from '@vitejs/plugin-react'
import cesium from 'vite-plugin-cesium'

export default vite.defineConfig(
{
    main: {},
    preload: {},
    renderer:
    {
        base: './',
        build:
        {
            outDir: path.resolve(__dirname, 'out/renderer'),
        },
        resolve:
        {
            alias:
            {
                '@renderer': path.resolve('src/renderer/src')
            }
        },
        plugins:
        [
            react(),
            cesium()
        ]
    }
})
