// Vue 3 app entry point — creates the app instance, wires up the router, and mounts to #app in index.html
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/main.css'; // global styles and Bootstrap Icons overrides

const app = createApp(App);
app.use(router); // register vue-router for SPA navigation
app.mount('#app');
