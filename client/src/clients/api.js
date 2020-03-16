
var client = require('./HttpClient');

export const stillAlive = async function () {
    let response = await client.get('/api/stillalive');
    return response.data;
}

export const register = async function (mode, online) {
    let response = await client.post('/api/register', {
        mode: mode,
        online: online,
    });
    return response.data;
}

export const pair = async function () {
    let response = await client.get('/api/pair');
    return response.data;
}

export const single = async function () {
    let response = await client.get('/api/single');
    return response.data;
}

export const game = async function (game_id) {
    let response = await client.post('/api/game', {
        game_id: game_id,
    });
    return response.data;
}

export const play = async function (x, y) {
    let response = await client.post('/api/play', {
        x: x,
        y: y,
    });
    return response.data;
}

export const exitApp = async function () {
    let response = await client.get('/api/exit');
    return response.data;
}
