import create from 'zustand'

const useAuthStore = create((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  
  setToken: (token) => set({ token }),
  
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
  
  login: (user, token) => set({ user, token, isAuthenticated: true }),
  
  checkAuth: () => {
    const token = localStorage.getItem('access_token')
    const user = localStorage.getItem('user')
    if (token && user) {
      set({ token, user: JSON.parse(user), isAuthenticated: true })
      return true
    }
    return false
  }
}))

export default useAuthStore
