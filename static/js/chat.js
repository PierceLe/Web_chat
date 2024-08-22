const hex2Arr = str => {
    if (!str) {
        return new Uint8Array()
    }
    const arr = []
    for (let i = 0, len = str.length; i < len; i += 2) {
        arr.push(parseInt(str.substr(i, 2), 16))
    }
    return new Uint8Array(arr)
}

const buf2Hex = buf => {
    return Array.from(new Uint8Array(buf))
        .map(x => ('00' + x.toString(16)).slice(-2))
        .join('')
}

const ecdhCreateKey = async() => {
    const keyPair = await window.crypto.subtle.generateKey(
        {
            name: 'ECDH',
            namedCurve: 'P-256'
        },
        true,
        ['deriveKey', 'deriveBits']
    )

    const privateKey = await window.crypto.subtle.exportKey(
        'jwk', keyPair.privateKey
    )

    const publicKey = await window.crypto.subtle.exportKey(
        'jwk', keyPair.publicKey
    )

    return {
        privateKey,
        publicKey
    }
}

async function createPairKey(){
    const { privateKey, publicKey } = await ecdhCreateKey()
    localStorage.setItem("e2e-prkey", JSON.stringify(privateKey));
    localStorage.setItem("e2e-pbkey", JSON.stringify(publicKey));
    return publicKey
}

const importKeyFromJson = (publicKeyJson) => {
    const publicKey = JSON.parse(publicKeyJson)
    return window.crypto.subtle.importKey(
        'jwk',
        publicKey,
        {
            name: 'ECDH',
            namedCurve: 'P-256'
        },
        true,
        publicKey.key_ops
    )
}

const getSharedSecret = (privateKey, publicKey) => {
    return window.crypto.subtle.deriveBits(
        {
            name: 'ECDH',
            namedCurve: 'P-256',
            public: publicKey
        },
        privateKey,
        256
    )
}

const aesCBCGenerateKey = async (sharedSecret) => {
    const key = await window.crypto.subtle.importKey(
        'raw',
        sharedSecret,
        {
            name: 'AES-CBC',
        },
        true,
        ['encrypt', 'decrypt']
    )

    return window.crypto.subtle.exportKey(
        'jwk',
        key,
        {
            name: 'AES-CBC',
        },
        true,
        ['encrypt', 'decrypt']
    )
}

const importKeyAESFromJson = (publicKeyJson) => {
    const publicKey = JSON.parse(publicKeyJson)
    return window.crypto.subtle.importKey(
        'jwk',
        publicKey,
        {
            name: 'AES-CBC',
        },
        true,
        publicKey.key_ops
    )
}

const iv = new Uint8Array([10, 54, 176, 89, 39, 95, 193, 191, 69, 111, 54, 155, 128, 42, 209, 127])
const aesCBCEncrypt = (key, content) => {
    return window.crypto.subtle.encrypt(
        {
            name: "AES-CBC",
            iv: iv,
        },
        key, 
        content
    )
}

const aesCBCDecrypt = (key, contentEncrypt) => {
    return window.crypto.subtle.decrypt(
        {
            name: "AES-CBC",
            iv: iv,
        },
        key, 
        contentEncrypt
    )
}

function stringToArrayBuffer(content){
    const encoder = new TextEncoder();
    const encodedText = encoder.encode(content);
    return encodedText.buffer; 
}

function arrayBufferToString(buffer) {
    const decoder = new TextDecoder();
    const text = decoder.decode(buffer);
    return text;
}

function arrayBufferToHex(arrayBuffer) {
    const uint8Array = new Uint8Array(arrayBuffer);
    return Array.prototype.map.call(uint8Array, x => ('00' + x.toString(16)).slice(-2)).join('');
}

function hexToArrayBuffer(hexString) {
    const bytes = new Uint8Array(hexString.match(/[\da-f]{2}/gi).map(function(h) {
        return parseInt(h, 16);
    }));
    return bytes.buffer;
}