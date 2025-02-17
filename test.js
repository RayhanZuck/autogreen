import fs from 'fs'
import path, { dirname } from 'path'
import assert from 'assert'
import { spawn } from 'child_process'
import syntaxError from 'syntax-error'
import { fileURLToPath } from 'url'
import { createRequire } from 'module'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const require = createRequire(__dirname)

let folders = ['.', ...Object.keys(require(path.join(__dirname, './package.json')).directories)]
let files = []
for (let folder of folders)
    for (let file of fs.readdirSync(folder).filter(v => v.endsWith('.js')))
        files.push(path.resolve(path.join(folder, file)))
for (let file of files) {
    if (file == __filename) continue
    console.error('Checking', file)
    const error = syntaxError(fs.readFileSync(file, 'utf8'), file, {
        sourceType: 'module',
        allowReturnOutsideFunction: true,
        allowAwaitOutsideFunction: true
    })
    if (error) assert.ok(error.length < 1, file + '\n\n' + error)
    assert.ok(file)
    console.log('Done', file)
}Commit ke-1
Commit ke-2
Commit ke-3
Commit ke-4
Commit ke-5
Commit ke-6
Commit ke-7
Commit ke-8
Commit ke-9
Commit ke-10
Commit ke-11
Commit ke-12
Commit ke-13
Commit ke-14
Commit ke-15
Commit ke-16
Commit ke-17
Commit ke-18
Commit ke-19
Commit ke-20
Commit ke-21
Commit ke-22
Commit ke-23
Commit ke-24
Commit ke-25
Commit ke-26
Commit ke-27
Commit ke-28
Commit ke-29
Commit ke-30
Commit ke-31
Commit ke-32
Commit ke-33
Commit ke-34
Commit ke-35
Commit ke-36
Commit ke-37
Commit ke-38
Commit ke-39
Commit ke-40
Commit ke-41
Commit ke-42
Commit ke-43
Commit ke-44
Commit ke-45
Commit ke-46
Commit ke-47
Commit ke-48
Commit ke-49
Commit ke-50
Commit ke-1
Commit ke-2
Commit ke-3
Commit ke-4
Commit ke-5
Commit ke-6
Commit ke-7
Commit ke-8
Commit ke-9
Commit ke-10
Commit ke-11
Commit ke-12
Commit ke-13
Commit ke-14
Commit ke-15
Commit ke-16
Commit ke-17
Commit ke-18
Commit ke-19
Commit ke-20
Commit ke-21
Commit ke-22
Commit ke-23
Commit ke-24
Commit ke-25
Commit ke-26
Commit ke-27
Commit ke-28
Commit ke-29
Commit ke-30
Commit ke-31
Commit ke-32
Commit ke-33
Commit ke-34
Commit ke-35
Commit ke-36
Commit ke-37
Commit ke-38
Commit ke-39
Commit ke-40
Commit ke-41
Commit ke-42
Commit ke-43
Commit ke-44
Commit ke-45
Commit ke-46
Commit ke-47
Commit ke-48
Commit ke-49
Commit ke-50
Commit ke-51
Commit ke-52
Commit ke-53
Commit ke-54
Commit ke-55
Commit ke-56
Commit ke-57
Commit ke-58
Commit ke-59
Commit ke-60
Commit ke-61
Commit ke-62
Commit ke-63
Commit ke-64
Commit ke-65
Commit ke-66
Commit ke-67
Commit ke-68
Commit ke-69
Commit ke-70
Commit ke-71
Commit ke-72
Commit ke-73
Commit ke-74
Commit ke-75
Commit ke-76
Commit ke-77
Commit ke-78
Commit ke-79
Commit ke-80
Commit ke-81
Commit ke-82
Commit ke-83
Commit ke-84
Commit ke-85
Commit ke-86
Commit ke-87
Commit ke-88
Commit ke-89
Commit ke-90
Commit ke-91
Commit ke-92
Commit ke-93
Commit ke-94
Commit ke-95
Commit ke-96
Commit ke-97
Commit ke-98
Commit ke-99
Commit ke-100
Commit ke-101
Commit ke-102
Commit ke-103
Commit ke-104
Commit ke-105
Commit ke-106
Commit ke-107
Commit ke-108
Commit ke-109
Commit ke-110
Commit ke-111
Commit ke-112
Commit ke-113
Commit ke-114
Commit ke-115
Commit ke-116
Commit ke-117
Commit ke-118
Commit ke-119
Commit ke-120
Commit ke-121
Commit ke-122
Commit ke-123
Commit ke-124
