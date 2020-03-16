var axios = require('axios');

var now = new Date().getTime();
localStorage.setItem('setupTime', now);

var axiosInstance = axios.create();

module.exports = axiosInstance;
