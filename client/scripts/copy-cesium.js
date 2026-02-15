import fs from 'node:fs'
import path from 'node:path'

const src = path.resolve('node_modules/cesium/Build/Cesium')
const dest = path.resolve('out/renderer/cesium')

fs.rmSync(dest, { recursive: true, force: true })
fs.mkdirSync(dest, { recursive: true })
fs.cpSync(src, dest, { recursive: true })

console.log('✔ Cesium assets copied to out/renderer/cesium')
