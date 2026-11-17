import { createRouter, createWebHistory } from 'vue-router';
import { isAuthenticated, userRole } from '@/store/auth';

// Views
import LandingView from '@/views/LandingView.vue';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import UserDashboardView from '@/views/UserDashboardView.vue';
import UserTreksView from '@/views/UserTreksView.vue';
import UserBookingsView from '@/views/UserBookingsView.vue';
import UserProfileView from '@/views/UserProfileView.vue';
import StaffDashboardView from '@/views/StaffDashboardView.vue';
import StaffTrekDetailView from '@/views/StaffTrekDetailView.vue';
import AdminDashboardView from '@/views/AdminDashboardView.vue';
import AdminTreksView from '@/views/AdminTreksView.vue';
import AdminStaffView from '@/views/AdminStaffView.vue';
import AdminUsersView from '@/views/AdminUsersView.vue';
import AdminBookingsView from '@/views/AdminBookingsView.vue';
import AdminReportsView from '@/views/AdminReportsView.vue';

// meta.requiresAuth = true means the route needs a valid JWT
// meta.role restricts the route to a specific user role
const routes = [
  // Public — accessible without login
  { path: '/', name: 'landing', component: LandingView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },

  // Trekker routes
  { path: '/dashboard', name: 'user-dashboard', component: UserDashboardView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/treks', name: 'user-treks', component: UserTreksView, meta: { requiresAuth: true, role: 'user' } },
  { path: '/my-bookings', name: 'user-bookings', component: UserBookingsView, meta: { requiresAuth: true, role: 'user' } },

  // Staff routes
  { path: '/staff', name: 'staff-dashboard', component: StaffDashboardView, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/staff/trek/:id', name: 'staff-trek-detail', component: StaffTrekDetailView, meta: { requiresAuth: true, role: 'staff' } },

  // Admin routes
  { path: '/admin', name: 'admin-dashboard', component: AdminDashboardView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/treks', name: 'admin-treks', component: AdminTreksView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/staff', name: 'admin-staff', component: AdminStaffView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/users', name: 'admin-users', component: AdminUsersView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/bookings', name: 'admin-bookings', component: AdminBookingsView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/reports', name: 'admin-reports', component: AdminReportsView, meta: { requiresAuth: true, role: 'admin' } },

  // Profile is shared — any logged-in role can access it
  { path: '/profile', name: 'profile', component: UserProfileView, meta: { requiresAuth: true } },

  // Fallback — unknown paths go back to landing
  { path: '/:pathMatch(.*)*', redirect: '/' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }; // scroll to top on every navigation
  },
});

// Global navigation guard — runs before every route change
router.beforeEach((to, from, next) => {
  const authed = isAuthenticated.value;
  const role = userRole.value;

  // redirect unauthenticated users to login, preserving the intended path as a query param
  if (to.meta.requiresAuth && !authed) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // if a logged-in user tries to access a route for a different role, send them to their own dashboard
  if (to.meta.role && to.meta.role !== role) {
    if (role === 'admin') return next({ name: 'admin-dashboard' });
    if (role === 'staff') return next({ name: 'staff-dashboard' });
    if (role === 'user') return next({ name: 'user-dashboard' });
    return next({ name: 'landing' });
  }

  // skip login/register pages if the user is already authenticated
  if ((to.name === 'login' || to.name === 'register') && authed) {
    if (role === 'admin') return next({ name: 'admin-dashboard' });
    if (role === 'staff') return next({ name: 'staff-dashboard' });
    if (role === 'user') return next({ name: 'user-dashboard' });
  }

  next();
});

export default router;
