// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config
const firebaseConfig = {
  apiKey: "AIzaSyBkmq_3ADDPBJPEeKxbB1gdAzA6w_nYXvw",
  authDomain: "dastabbej.firebaseapp.com",
  projectId: "dastabbej",
  storageBucket: "dastabbej.firebasestorage.app",
  messagingSenderId: "551200937246",
  appId: "1:551200937246:web:01e8d518f53fc5241e650f",
  measurementId: "G-W3XL93BPH1"
};

firebase.initializeApp(firebaseConfig);

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  // Customize notification here
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/icons/icon-192x192.png' // You might need to add an icon later
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// PWA: Basic fetch handler to allow installability
self.addEventListener('fetch', (event) => {
  // basic passthrough
  event.respondWith(fetch(event.request));
});
