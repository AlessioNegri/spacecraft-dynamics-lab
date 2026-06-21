import fs from 'node:fs'
import path from 'node:path'

const src = path.resolve('node_modules/cesium/Build/Cesium')
const dest = path.resolve('out/renderer/cesium')

fs.rmSync(dest, { recursive: true, force: true })
fs.mkdirSync(dest, { recursive: true })
fs.cpSync(src, dest, { recursive: true })

console.log('✔ Cesium assets copied to out/renderer/cesium')

const splash = path.resolve('src/renderer/SpacecraftDynamicsLab.png')
const image = path.resolve('src/renderer/splash.html')
const destination = path.resolve('out/renderer')

fs.copyFileSync(splash, path.join(destination, 'SpacecraftDynamicsLab.png'))
fs.copyFileSync(image, path.join(destination, 'splash.html'))

console.log('✔ Splash assets copied to out/renderer/')
