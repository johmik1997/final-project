<template>
  <div class="homepage min-h-screen bg-white dark:bg-slate-900 transition-colors duration-300">
    <!-- Navbar with Search -->
    <nav class="sticky top-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-gray-200 dark:border-white/10 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo / Home -->
          <button @click="scrollTo('hero')" class="flex items-center space-x-2 hover:opacity-80 transition">
            <img 
              src='../assets/logolib.jpg'
              alt="Logo" 
              class="w-12 h-12 rounded-full object-cover border-2 border-amber-500 shadow-lg shadow-amber-500/30"
            >
            <span class="text-slate-900 dark:text-white font-bold text-lg">HU<span class="text-amber-500">-DLRBS</span></span>
          </button>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-4">
            <button @click="scrollTo('hero')" class="text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium">Home</button>
            
            <!-- Campus Dropdown -->
            <div class="relative" @mouseenter="showCampus = true" @mouseleave="showCampus = false">
              <button class="flex items-center space-x-1 text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium py-2">
                <span>Campus</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              <div v-show="showCampus" class="absolute left-0 top-full w-56 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-gray-200 dark:border-white/10 overflow-hidden">
                <div class="p-2">
                  <button v-for="campus in campuses" :key="campus.id" @click="selectCampus(campus)" class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 text-slate-700 dark:text-slate-300 hover:text-amber-500 dark:hover:text-white transition text-sm">
                    {{ campus.name }}
                  </button>
                </div>
              </div>
            </div>
            
            <button @click="scrollTo('materials')" class="text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium">Materials</button>
            <button @click="scrollTo('about')" class="text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium">About</button>
            <button @click="scrollTo('staff')" class="text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium">Administration</button>
            <button @click="scrollTo('help')" class="text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition text-sm font-medium">Help</button>
          </div>

          <!-- Search Bar -->
          <div class="hidden md:flex items-center bg-gray-100 dark:bg-slate-800 rounded-full px-4 py-1.5 border border-gray-200 dark:border-white/10 w-64 transition-colors duration-300">
            <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input type="text" placeholder="Search books, resources..." v-model="searchQuery" class="bg-transparent text-slate-800 dark:text-white text-sm ml-2 outline-none w-full placeholder-slate-400 dark:placeholder-slate-500">
          </div>

          <!-- Auth Buttons + Theme Toggle + Mobile Menu Toggle -->
          <div class="flex items-center space-x-2">
            <!-- Theme Toggle -->
            <ThemeToggle id="homepage-theme-toggle" />

            <button @click="$router.push('/login')" class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-red-500 text-white text-sm font-semibold hover:shadow-lg transition">
              Sign In
            </button>
            
            <!-- Mobile Menu Button -->
            <button 
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition"
              aria-label="Menu"
            >
              <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
              <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Mobile Navigation Menu -->
      <transition name="mobile-menu">
        <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-200 dark:border-white/10 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md">
          <div class="px-4 py-3 space-y-2">
            <button @click="scrollTo('hero'); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium">
              Home
            </button>
            
            <!-- Mobile Campus Dropdown -->
            <div class="relative">
              <button 
                @click="mobileShowCampus = !mobileShowCampus"
                class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium"
              >
                <span>Campus</span>
                <svg class="w-4 h-4 transition-transform duration-200" :class="{ 'rotate-180': mobileShowCampus }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </button>
              <div v-show="mobileShowCampus" class="pl-4 space-y-1 mt-1">
                <button v-for="campus in campuses" :key="campus.id" @click="selectCampus(campus); mobileMenuOpen = false; mobileShowCampus = false" class="w-full text-left px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-white/10 text-slate-600 dark:text-slate-400 hover:text-amber-500 transition text-sm">
                  {{ campus.name }}
                </button>
              </div>
            </div>
            
            <button @click="scrollTo('materials'); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium">Materials</button>
            <button @click="scrollTo('about'); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium">About</button>
            <button @click="scrollTo('staff'); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium">Administration</button>
            <button @click="scrollTo('help'); mobileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-lg text-slate-700 dark:text-slate-300 hover:text-amber-500 hover:bg-gray-100 dark:hover:bg-white/10 transition text-sm font-medium">Help</button>
            
            <!-- Mobile Search -->
            <div class="pt-2 border-t border-gray-200 dark:border-white/10 mt-2">
              <div class="flex items-center bg-gray-100 dark:bg-slate-800 rounded-full px-4 py-2 border border-gray-200 dark:border-white/10">
                <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <input type="text" placeholder="Search books..." v-model="searchQuery" class="bg-transparent text-slate-800 dark:text-white text-sm ml-2 outline-none w-full placeholder-slate-400 dark:placeholder-slate-500">
              </div>
            </div>
          </div>
        </div>
      </transition>
    </nav>

    <!-- Hero Section -->
    <section id="hero" class="relative h-[550px] md:h-[600px] overflow-hidden">
      <div class="absolute inset-0">
        <div v-for="(slide, idx) in heroSlides" :key="idx" class="absolute inset-0 transition-opacity duration-1000" :class="currentSlide === idx ? 'opacity-100' : 'opacity-0'">
          <img :src="slide.image" class="w-full h-full object-cover">
          <div class="absolute inset-0 bg-gradient-to-r from-slate-900 via-slate-900/70 to-transparent"></div>
        </div>
      </div>
      
      <div class="relative h-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center">
        <div class="max-w-2xl">
          <transition name="slide-text" mode="out-in">
            <div :key="currentSlide" class="relative">
              <h1 class="text-4xl md:text-6xl font-bold text-white mb-4">
                {{ heroSlides[currentSlide].title }}
              </h1>
              <p class="text-lg text-slate-300 mb-6 leading-relaxed">
                {{ heroSlides[currentSlide].description }}
              </p>
            </div>
          </transition>
          <div class="flex flex-wrap gap-3">
            <button @click="scrollTo('materials')" class="px-5 py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold hover:shadow-xl transition flex items-center space-x-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
              <span>Browse Materials</span>
            </button>
            <button @click="scrollTo('campus-section')" class="px-5 py-2.5 rounded-lg border border-white/30 text-white font-semibold hover:bg-white/10 transition flex items-center space-x-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
              <span>Explore Campuses</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Slide Dots -->
      <div class="absolute bottom-5 left-1/2 transform -translate-x-1/2 flex space-x-2">
        <button v-for="(_, idx) in heroSlides" :key="idx" @click="currentSlide = idx" class="transition-all duration-300" :class="currentSlide === idx ? 'w-8 h-2 bg-amber-500 rounded-full' : 'w-2 h-2 bg-white/50 rounded-full'"></button>
      </div>
    </section>

    <!-- Campus Section -->
    <section id="campus-section" class="py-16 bg-slate-100 dark:bg-slate-900 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-10">
          <span class="text-amber-500 text-sm font-semibold uppercase tracking-wider">Our Campuses</span>
          <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-2 transition-colors duration-300">Explore Campus Libraries</h2>
          <p class="text-slate-500 dark:text-slate-400 mt-2 transition-colors duration-300">Select a campus to explore its libraries</p>
        </div>

        <!-- Campus Tabs -->
        <div class="flex flex-wrap justify-center gap-4 mb-12">
          <button 
            v-for="campus in campuses" 
            :key="campus.id" 
            @click="selectCampus(campus)"
            class="group relative px-6 py-3 rounded-xl transition-all duration-300"
            :class="selectedCampus?.id === campus.id 
              ? 'bg-gradient-to-r from-amber-500 to-red-500 text-white shadow-lg shadow-amber-500/25' 
              : 'bg-white dark:bg-slate-800/50 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white border border-gray-200 dark:border-white/5'"
          >
            <div class="flex items-center space-x-2">
              <span class="text-xl">{{ campus.icon }}</span>
              <span class="font-semibold">{{ campus.name }}</span>
            </div>
            <div v-if="selectedCampus?.id === campus.id" class="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-amber-400 rounded-full"></div>
          </button>
        </div>

        <!-- Dynamic Campus Content -->
        <transition name="campus-fade" mode="out-in">
          <div v-if="selectedCampus" :key="selectedCampus.id" class="relative">
            <div class="grid mb-8 max-w-sm mx-auto">
              <div class="text-center p-3 bg-white dark:bg-slate-800/40 rounded-xl border border-gray-200 dark:border-white/5 transition-colors duration-300">
                <div class="text-2xl font-bold text-amber-500">{{ selectedCampus.libraries.length }}</div>
                <div class="text-slate-500 dark:text-slate-400 text-xs transition-colors duration-300">Libraries</div>
              </div>
            </div>

            <!-- Library Carousel -->
            <div class="relative">
              <button @click="prevLibrary" class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 w-10 h-10 rounded-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-white/20 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-slate-700 hover:border-amber-500/50 transition-all duration-300 shadow-sm">
                <svg class="w-5 h-5 text-slate-700 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                </svg>
              </button>
              
              <button @click="nextLibrary" class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 w-10 h-10 rounded-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-white/20 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-slate-700 hover:border-amber-500/50 transition-all duration-300 shadow-sm">
                <svg class="w-5 h-5 text-slate-700 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
              </button>

              <transition name="library-fade" mode="out-in">
                <div :key="currentLibrary?.name" class="bg-white dark:bg-gradient-to-br dark:from-slate-800 dark:to-slate-900 rounded-2xl border border-gray-200 dark:border-white/10 overflow-hidden shadow-sm transition-colors duration-300">
                  <div class="grid md:grid-cols-2 gap-6 p-6">
                    <div class="relative h-64 md:h-80 rounded-xl overflow-hidden">
                      <img :src="currentLibrary?.image" :alt="currentLibrary?.name" class="w-full h-full object-cover transition-transform duration-500">
                      <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                        <div class="flex justify-center items-center">
                          <div class="flex space-x-1">
                            <div v-for="(lib, idx) in selectedCampus.libraries" :key="idx" 
                                 class="h-1 rounded-full transition-all duration-300 cursor-pointer"
                                 :class="libraryIndex === idx ? 'w-6 bg-amber-500' : 'w-3 bg-white/30'"
                                 @click="libraryIndex = idx"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="flex flex-col justify-center">
                      <div class="inline-block px-3 py-1 bg-amber-500/20 rounded-full text-amber-600 dark:text-amber-400 text-xs font-semibold w-fit mb-3">
                        {{ selectedCampus.name }}
                      </div>
                      <h3 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-3 transition-colors duration-300">{{ currentLibrary?.name }}</h3>
                      <p class="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed transition-colors duration-300">{{ currentLibrary?.description }}</p>
                      <div class="flex items-center space-x-4 text-sm">
                        <div class="flex items-center space-x-1 text-slate-500 dark:text-slate-400">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                          <span>{{ currentLibrary?.materials }}+ materials</span>
                        </div>
                        <div class="flex items-center space-x-1 text-slate-500 dark:text-slate-400">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                          <span>{{ currentLibrary?.hours }}</span>
                        </div>
                      </div>
                      <button @click="viewLibraryCollections(currentLibrary)" class="mt-5 px-4 py-2 rounded-lg bg-amber-500/10 dark:bg-amber-500/20 text-amber-600 dark:text-amber-400 font-semibold text-sm hover:bg-amber-500/20 dark:hover:bg-amber-500/30 transition w-fit border border-amber-500/20">
                        View Collections →
                      </button>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </transition>
      </div>
    </section>

    <!-- MATERIALS SECTION -->
    <section id="materials" class="py-16 bg-gray-50 dark:bg-slate-800/20 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <span class="text-amber-500 text-sm font-semibold uppercase tracking-wider">Library Collection</span>
          <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-2 transition-colors duration-300">Discover Our Collection</h2>
          <p class="text-slate-500 dark:text-slate-400 mt-2 transition-colors duration-300">Browse books, magazines, theses, and research materials</p>
        </div>

        <!-- Category Tabs -->
        <div class="flex flex-wrap justify-center gap-3 mb-12">
          <button 
            v-for="cat in materialCategories" 
            :key="cat.value" 
            @click="selectedCategory = cat.value"
            class="group relative px-6 py-3 rounded-xl transition-all duration-300"
            :class="selectedCategory === cat.value 
              ? 'bg-gradient-to-r from-amber-500 to-red-500 text-white shadow-lg shadow-amber-500/25' 
              : 'bg-white dark:bg-slate-800/50 text-slate-600 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white border border-gray-200 dark:border-white/5'"
          >
            <div class="flex items-center space-x-2">
              <span class="text-xl">{{ cat.icon }}</span>
              <span class="font-semibold">{{ cat.label }}</span>
            </div>
            <div v-if="selectedCategory === cat.value" class="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-8 h-1 bg-amber-400 rounded-full"></div>
          </button>
        </div>

        <!-- Unified Materials Grid -->
        <div>
          <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
            <div>
              <h3 class="text-lg font-semibold text-slate-700 dark:text-slate-300 transition-colors duration-300">
                <span class="text-amber-500">{{ getCategoryLabel(selectedCategory) }}</span>
                <span class="text-slate-400 dark:text-slate-500 text-sm ml-2">({{ filteredMaterials.length }} items)</span>
              </h3>
            </div>
            <div class="flex gap-2">
              <select v-model="sortBy" class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-white/10 rounded-lg px-3 py-1.5 text-slate-700 dark:text-slate-300 text-sm focus:outline-none focus:border-amber-500/50 transition-colors duration-300">
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="title">Title A-Z</option>
                <option value="rating">Top Rated</option>
              </select>
            </div>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            <div v-for="item in sortedMaterials" :key="item.id" class="group relative bg-white dark:bg-slate-800/40 rounded-xl border border-gray-200 dark:border-white/5 overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-md dark:hover:shadow-none hover:border-amber-500/30 dark:hover:border-amber-500/30">
              <!-- Featured Badge -->
              <div v-if="item.rating >= 4.8" class="absolute top-3 left-3 z-10">
                <div class="bg-gradient-to-r from-amber-500 to-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full shadow-lg">
                  ⭐ Featured
                </div>
              </div>
              
              <!-- Book Cover Image -->
              <div class="relative h-48 overflow-hidden bg-gradient-to-br from-gray-100 dark:from-slate-700 to-gray-200 dark:to-slate-800">
                <img 
                  :src="getBookImage(item.title, item.category)" 
                  :alt="item.title" 
                  class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                >
                <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-60"></div>
              </div>
              
              <!-- Content -->
              <div class="p-4">
                <h4 class="text-slate-900 dark:text-white font-bold text-base line-clamp-1 transition-colors duration-300">{{ item.title }}</h4>
                <p class="text-amber-500 dark:text-amber-400 text-sm">{{ item.author }}</p>
                
                <!-- Rating Stars -->
                <div class="flex items-center space-x-1 mt-2">
                  <div class="flex text-amber-500 text-xs">
                    <span v-for="n in 5" :key="n">
                      <svg v-if="n <= Math.floor(item.rating)" class="w-3.5 h-3.5 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                      <svg v-else class="w-3.5 h-3.5 text-gray-300 dark:text-slate-600" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                    </span>
                  </div>
                  <span class="text-slate-400 dark:text-slate-400 text-xs">({{ item.reviews }})</span>
                  <span class="text-slate-400 dark:text-slate-500 text-xs">• {{ item.year }}</span>
                </div>
                
                <!-- Description -->
                <p class="text-slate-500 dark:text-slate-400 text-xs mt-2 line-clamp-2 transition-colors duration-300">{{ item.description.substring(0, 80) }}...</p>
                
                <!-- Status Badge -->
                <div class="mt-3">
                  <span :class="['text-xs px-2 py-0.5 rounded-full', item.status === 'available' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400' : 'bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-400']">
                    {{ item.status === 'available' ? 'Available' : 'Borrowed' }}
                  </span>
                </div>
                
                <!-- Details Button -->
                <button 
                  @click="handleAction(item.type === 'digital' ? 'read' : 'borrow', item.title)" 
                  class="mt-4 w-full py-2 rounded-lg bg-amber-50 dark:bg-amber-500/10 border border-amber-300 dark:border-amber-500/30 text-amber-600 dark:text-amber-400 text-sm font-semibold hover:bg-amber-100 dark:hover:bg-amber-500/20 hover:border-amber-400 dark:hover:border-amber-500/50 transition-all duration-300 flex items-center justify-center space-x-2 group/btn"
                >
                  <span>Details</span>
                  <svg class="w-4 h-4 transition-transform duration-200 group-hover/btn:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-if="filteredMaterials.length === 0" class="text-center py-16">
            <div class="w-20 h-20 mx-auto bg-gray-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-4">
              <span class="text-3xl">📚</span>
            </div>
            <p class="text-slate-500 dark:text-slate-400">No materials found in this category.</p>
            <p class="text-slate-400 dark:text-slate-500 text-sm mt-1">Try adjusting your search or select a different category.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-16 bg-white dark:bg-slate-900 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span class="text-amber-500 text-sm font-semibold uppercase tracking-wider">About Our System</span>
            <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-2 mb-4 transition-colors duration-300">HU Digital Library Reservation & Book Borrowing System</h2>
            <p class="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed transition-colors duration-300">
              The HU-DLRBS is a comprehensive digital platform designed to modernize library services across all Hawassa University campuses. It provides seamless access to academic resources for students, faculty, and staff, improving efficiency in reservation and borrowing processes.
            </p>
            <p class="text-slate-600 dark:text-slate-300 mb-4 leading-relaxed transition-colors duration-300">
              With 80,000+ books and 20,000+ institutional repository resources, the system supports education and research through reliable and innovative technology.
            </p>
            <div class="flex items-center space-x-6 mt-4">
              <div><span class="text-2xl font-bold text-amber-500">80K+</span><span class="text-slate-500 dark:text-slate-400 text-sm ml-1">Materials</span></div>
              <div><span class="text-2xl font-bold text-amber-500">9</span><span class="text-slate-500 dark:text-slate-400 text-sm ml-1">Libraries</span></div>
            </div>
          </div>
          <div class="bg-gradient-to-br from-amber-500/10 to-red-500/10 rounded-2xl p-6 border border-amber-200 dark:border-white/10">
            <img src="../assets/libr1.jpg" alt="Library" class="rounded-xl w-full h-64 object-cover">
          </div>
        </div>
      </div>
    </section>

    <!-- Administration / Staff Section -->
    <section id="staff" class="py-16 bg-gray-50 dark:bg-slate-800/20 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <span class="text-amber-500 text-sm font-semibold uppercase tracking-wider">Leadership</span>
          <h2 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mt-2 transition-colors duration-300">Library Administration & Staff</h2>
          <p class="text-slate-500 dark:text-slate-400 mt-2 transition-colors duration-300">Meet the team managing your library experience</p>
        </div>

        <div class="relative max-w-4xl mx-auto">
          <button @click="prevStaff" class="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 md:-translate-x-12 z-10 w-10 h-10 rounded-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-white/20 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-slate-700 transition shadow-sm">
            <svg class="w-5 h-5 text-slate-700 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
          </button>
          <button @click="nextStaff" class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 md:translate-x-12 z-10 w-10 h-10 rounded-full bg-white dark:bg-slate-800 border border-gray-200 dark:border-white/20 flex items-center justify-center hover:bg-gray-50 dark:hover:bg-slate-700 transition shadow-sm">
            <svg class="w-5 h-5 text-slate-700 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
          </button>

          <div class="relative overflow-hidden rounded-2xl min-h-[450px]">
            <div class="flex transition-transform duration-500 ease-out" :style="{ transform: `translateX(-${staffIndex * 100}%)` }">
              <div v-for="staff in staffMembers" :key="staff.id" class="w-full flex-shrink-0">
                <div class="bg-white dark:bg-slate-800/60 rounded-2xl border border-gray-200 dark:border-white/10 overflow-hidden mx-4 shadow-sm transition-colors duration-300">
                  <div class="grid md:grid-cols-2 gap-0">
                    <div class="h-80 md:h-auto relative overflow-hidden">
                      <img :src="staff.image" :alt="staff.name" class="w-full h-full object-cover">
                      <div class="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent md:hidden"></div>
                    </div>
                    <div class="p-6 md:p-8 flex flex-col justify-center">
                      <div class="inline-block px-3 py-1 bg-amber-500/10 dark:bg-amber-500/20 rounded-full text-amber-600 dark:text-amber-400 text-xs font-semibold w-fit mb-3">
                        {{ staff.role }}
                      </div>
                      <h3 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-2 transition-colors duration-300">{{ staff.name }}</h3>
                      <p class="text-slate-600 dark:text-slate-300 leading-relaxed mb-4 transition-colors duration-300">{{ staff.bio }}</p>
                      <div class="flex flex-col space-y-2 text-sm text-slate-500 dark:text-slate-400 transition-colors duration-300">
                        <div class="flex items-center space-x-2">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                          <span>{{ staff.email }}</span>
                        </div>
                        <div class="flex items-center space-x-2">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                          <span>{{ staff.experience }}+ years of experience</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-center space-x-2 mt-6">
            <button v-for="(_, idx) in staffMembers" :key="idx" @click="staffIndex = idx" class="h-2 rounded-full transition-all duration-300" :class="staffIndex === idx ? 'w-8 bg-amber-500' : 'w-2 bg-gray-300 dark:bg-white/30'"></button>
          </div>
        </div>
      </div>
    </section>

    <!-- Help Section -->
    <section id="help" class="py-20 bg-white dark:bg-gradient-to-br dark:from-slate-900 dark:to-slate-800 transition-colors duration-300">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="text-center mb-14">
          <span class="text-amber-500 text-sm font-semibold uppercase tracking-wider">Support</span>
          <h2 class="text-4xl font-bold text-slate-900 dark:text-white mt-3 transition-colors duration-300">How to Use the System</h2>
          <p class="text-slate-500 dark:text-slate-400 mt-3 max-w-xl mx-auto transition-colors duration-300">Follow these simple steps to search, reserve, and borrow library materials easily.</p>
        </div>

        <!-- Steps -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-14">
          <div v-for="(step, idx) in helpSteps" :key="idx" class="group text-center p-5 bg-gray-50 dark:bg-slate-800/60 rounded-xl border border-gray-200 dark:border-white/10 hover:border-amber-500/40 hover:-translate-y-1 transition-all duration-300">
            <div class="w-14 h-14 mx-auto bg-amber-100 dark:bg-amber-500/20 rounded-full flex items-center justify-center mb-4">
              <span class="text-amber-600 dark:text-amber-500 font-bold text-xl">{{ idx + 1 }}</span>
            </div>
            <p class="text-slate-800 dark:text-white font-semibold transition-colors duration-300">{{ step.title }}</p>
            <p class="text-slate-500 dark:text-slate-400 text-xs mt-2 transition-colors duration-300">{{ step.desc }}</p>
          </div>
        </div>

        <!-- FAQ Section -->
        <div class="bg-gray-50 dark:bg-slate-800/40 rounded-2xl border border-gray-200 dark:border-white/10 overflow-hidden backdrop-blur-sm transition-colors duration-300">
          <div class="p-6 border-b border-gray-200 dark:border-white/10 bg-white dark:bg-slate-800/60 transition-colors duration-300">
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 rounded-full bg-amber-100 dark:bg-amber-500/20 flex items-center justify-center">
                <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M12 21a9 9 0 100-18 9 9 0 000 18z"></path>
                </svg>
              </div>
              <h3 class="text-xl font-bold text-slate-900 dark:text-white transition-colors duration-300">Frequently Asked Questions</h3>
            </div>
            <p class="text-slate-500 dark:text-slate-400 text-sm mt-2 ml-11 transition-colors duration-300">Find quick answers to common questions about our library system</p>
          </div>
          
          <div class="divide-y divide-gray-200 dark:divide-white/5 transition-colors duration-300">
            <div v-for="(faq, idx) in faqs" :key="idx" class="faq-item">
              <button
                @click="openFaq = openFaq === idx ? null : idx"
                class="w-full flex justify-between items-center p-5 text-left hover:bg-gray-100 dark:hover:bg-white/5 transition-all duration-300 group"
              >
                <div class="flex items-start space-x-3">
                  <div class="w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-500/10 flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:bg-amber-200 dark:group-hover:bg-amber-500/20 transition-colors">
                    <span class="text-amber-600 dark:text-amber-400 text-xs font-bold">{{ idx + 1 }}</span>
                  </div>
                  <span class="text-slate-700 dark:text-white font-medium group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors duration-200">
                    {{ faq.q }}
                  </span>
                </div>
                
                <div class="flex-shrink-0 ml-4">
                  <svg 
                    class="w-5 h-5 transition-all duration-300 transform"
                    :class="openFaq === idx 
                      ? 'rotate-90 text-amber-500' 
                      : 'rotate-0 text-slate-400 group-hover:text-amber-500 group-hover:translate-x-0.5'"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                </div>
              </button>

              <transition name="faq-expand">
                <div v-show="openFaq === idx">
                  <div class="px-5 pb-5 pl-14">
                    <div class="relative">
                      <div class="absolute left-0 top-0 bottom-0 w-0.5 bg-gradient-to-b from-amber-500/50 to-amber-500/0"></div>
                      <p class="text-slate-600 dark:text-slate-300 text-sm leading-relaxed pl-4 transition-colors duration-300">
                        {{ faq.a }}
                      </p>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>

          <div class="p-4 bg-white dark:bg-slate-800/30 border-t border-gray-200 dark:border-white/5 text-center transition-colors duration-300">
            <p class="text-xs text-slate-500 dark:text-slate-500">
              Can't find your answer? <button @click="showHelpModal = true" class="text-amber-500 hover:text-amber-600 dark:hover:text-amber-300 transition-colors">Contact our support team</button>
            </p>
          </div>
        </div>

        <!-- CTA -->
        <div class="text-center mt-10">
          <button @click="showHelpModal = true" class="px-7 py-3 rounded-full bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 inline-flex items-center space-x-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01"></path>
            </svg>
            <span>Need More Help? Contact Support</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 dark:bg-slate-950 border-t border-gray-700 dark:border-white/10 py-8 transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-400 dark:text-slate-400 text-sm">
        <p>© 2024 Hawassa University - Digital Library Reservation and Book Borrowing System (HU-DLRBS)</p>
        <p class="mt-2">Hawassa, Ethiopia | library@hu.edu.et | +251 46 220 5168</p>
      </div>
    </footer>

    <!-- Login Prompt Modal -->
    <div v-if="showLoginPrompt" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showLoginPrompt = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-sm w-full mx-4 border border-gray-200 dark:border-white/20 transform transition-all duration-300 scale-100 shadow-xl">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto bg-amber-100 dark:bg-amber-500/20 rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path></svg>
          </div>
          <h3 class="text-slate-900 dark:text-white text-xl font-bold mb-2">Login Required</h3>
          <p class="text-slate-600 dark:text-slate-300 mb-6">You need to sign in to {{ pendingAction }} "{{ pendingItemTitle }}"</p>
          <div class="flex space-x-3">
            <button @click="showLoginPrompt = false" class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-white/20 text-slate-700 dark:text-white hover:bg-gray-100 dark:hover:bg-white/10 transition">Cancel</button>
            <button @click="$router.push('/login')" class="flex-1 px-4 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold hover:shadow-lg transition">Sign In</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Help Modal -->
    <div v-if="showHelpModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50" @click.self="showHelpModal = false">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 max-w-md w-full mx-4 border border-gray-200 dark:border-white/20 shadow-xl transition-colors duration-300">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-slate-900 dark:text-white text-xl font-bold">Contact Support</h3>
          <button @click="showHelpModal = false" class="text-slate-400 hover:text-slate-600 dark:hover:text-white transition">✕</button>
        </div>
        <div class="space-y-4">
          <div class="flex items-center space-x-3 text-slate-600 dark:text-slate-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            <span>library@hu.edu.et</span>
          </div>
          <div class="flex items-center space-x-3 text-slate-600 dark:text-slate-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            <span>+251 46 220 5168</span>
          </div>
          <div class="flex items-center space-x-3 text-slate-600 dark:text-slate-300">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            <span>3F2W+CQH, Hawassa</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import ThemeToggle from '@/components/ThemeToggle.vue';

const router = useRouter();
import referal from '@/assets/referal.jpg';
import referal2 from '@/assets/referal2.jpg';
import libr1Image from '@/assets/libr1.jpg';
import hu12Image from '@/assets/hu12.jpg';
import hul3Image from '@/assets/lib2.png';
import tewl from '@/assets/tew.jpg';
import comp from '@/assets/comp.jpg';
import iot from '@/assets/iot.jpg';
import wondo from '@/assets/wondo.jpg';
import awada from '@/assets/awada.jpg';
import agri from '@/assets/agri.jpg';

// Hero Slides
const heroSlides = ref([
  { 
    image: libr1Image,
    title: 'Discover, Borrow, and\nRead Smarter',
    description: 'Hawassa University\'s digital library system — access thousands of books, journals, and resources across all campuses.'
  },
  { 
    image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=1600&h=600&fit=crop',
    title: 'Digital Resources\nAt Your Fingertips',
    description: 'Access e-books, research papers, and academic journals 24/7 from anywhere in the world.'
  },
  { 
    image: referal2,
    title: 'Seamless Library\nManagement',
    description: 'Reserve books, track due dates, and manage your borrowing history all in one place.'
  }
]);
const currentSlide = ref(0);
let slideshowInterval;

// Help Steps
const helpSteps = ref([
  { title: 'Search', desc: 'Use search bar or browse catalog' },
  { title: 'Reserve / Read', desc: 'Login to borrow or read online' },
  { title: 'Borrow', desc: 'Pick up from campus library' },
  { title: 'Return / Renew', desc: 'Return or renew online' }
]);

// Campus Data
const campuses = ref([
  { 
    id: 1, name: 'Main Campus', icon: '🏛️', totalMaterials: 68, students: 15000,
    libraries: [
      { name: 'Main Library', description: 'Central library with comprehensive collections across all disciplines. Features study spaces, computer labs, and a 24/7 reading hall.', materials: '45,000', hours: '8am - 10pm', image: libr1Image },
      { name: 'College of Law and Governance Library', description: 'Provides legal texts, case studies, and governance-related resources to support students and researchers in law, policy, and public administration.', materials: '15,000', hours: '24/7', image: hu12Image },
      { name: 'College of Education Library', description: 'Supports teaching and learning in education by offering books, journals, and materials focused on pedagogy, curriculum development, and teacher training.', materials: '12,000', hours: '9am - 6pm', image: hul3Image },
      { name: 'College of Social Sciences and Humanities Library', description: 'Offers resources in areas such as history, sociology, languages, and philosophy to support research and academic work in social and human studies.', materials: '12,000', hours: '9am - 6pm', image: hul3Image },
      { name: 'College of Natural and Computational Sciences Library', description: 'Contains scientific and technical materials in fields like mathematics, physics, chemistry, biology, and computer science.', materials: '12,000', hours: '9am - 6pm', image: hul3Image }
    ] 
  },
  { 
    id: 2, name: 'Institute of Technology', icon: '⚙️', totalMaterials: 42, students: 8500,
    libraries: [
      { name: 'Institute of Technology Library', description: 'Supports engineering and technology programs with access to technical books, research papers, and digital resources in various engineering fields.', materials: '25,000', hours: '8am - 8pm', image: iot }
    ] 
  },
  { 
    id: 3, name: 'Medicine and Health Campus', icon: '🏥', totalMaterials: 31, students: 6200,
    libraries: [
      { name: 'College of Medicine and Health Sciences Library', description: 'Offers medical and health-related materials, including textbooks, journals, and research resources for students and professionals in healthcare.', materials: '18,000', hours: '8am - 8pm', image: referal2 }
    ] 
  },
  { 
    id: 4, name: 'Awada Campus', icon: '🏢', totalMaterials: 31, students: 6200,
    libraries: [
      { name: 'Awada College of Business and Economics Library', description: 'Provides resources in business, management, accounting, and economics to support academic and practical knowledge in commerce and finance.', materials: '18,000', hours: '8am - 8pm', image: awada }
    ] 
  },
  { 
    id: 5, name: 'Agricultural Campus', icon: '🌾', totalMaterials: 31, students: 6200,
    libraries: [
      { name: 'College of Agriculture Library', description: 'Provides specialized resources in agriculture, including crop science, animal production, soil science, and sustainable farming practices.', materials: '18,000', hours: '8am - 8pm', image: agri }
    ] 
  },
  { 
    id: 6, name: 'Wondo genet Campus', icon: '🌿', totalMaterials: 31, students: 6200,
    libraries: [
      { name: 'Wondo Genet College of Forestry & Natural Resources Library', description: 'Specializes in forestry, environmental science, and natural resource management, supporting research in conservation and sustainable development.', materials: '18,000', hours: '8am - 8pm', image: wondo }
    ] 
  },
]);

// Mobile menu state
const mobileMenuOpen = ref(false);
const mobileShowCampus = ref(false);

// Campus and Library state
const selectedCampus = ref(campuses.value[0]);
const libraryIndex = ref(0);
let libraryInterval;

const currentLibrary = computed(() => {
  return selectedCampus.value?.libraries[libraryIndex.value] || null;
});

function selectCampus(campus) {
  selectedCampus.value = campus;
  libraryIndex.value = 0;
  showCampus.value = false;
  mobileShowCampus.value = false;
  
  const section = document.getElementById('campus-section');
  if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  if (libraryInterval) clearInterval(libraryInterval);
  libraryInterval = setInterval(() => {
    if (selectedCampus.value?.libraries.length) {
      libraryIndex.value = (libraryIndex.value + 1) % selectedCampus.value.libraries.length;
    }
  }, 30000);
}

function nextLibrary() {
  if (selectedCampus.value?.libraries.length) {
    libraryIndex.value = (libraryIndex.value + 1) % selectedCampus.value.libraries.length;
  }
}

function prevLibrary() {
  if (selectedCampus.value?.libraries.length) {
    libraryIndex.value = (libraryIndex.value - 1 + selectedCampus.value.libraries.length) % selectedCampus.value.libraries.length;
  }
}

const showCampus = ref(false);
const searchQuery = ref('');
const sortBy = ref('newest');

// Material Categories
const materialCategories = [
  { value: 'books', label: 'Books', icon: '📚' },
  { value: 'magazine', label: 'Magazine', icon: '📰' },
  { value: 'thesis', label: 'Thesis', icon: '🎓' },
  { value: 'research', label: 'Research Book', icon: '🔬' }
];
const selectedCategory = ref('books');

// All Materials Data
const allMaterials = ref([
  { id: 1, title: 'Introduction to Algorithms', author: 'Thomas H. Cormen', rating: 4.8, reviews: 342, description: 'Comprehensive guide to algorithms and data structures. A must-read for computer science students.', category: 'books', type: 'physical', status: 'available', year: 2022 },
  { id: 2, title: 'Database Systems', author: 'Abraham Silberschatz', rating: 4.7, reviews: 218, description: 'Complete coverage of database design and implementation. Industry standard reference.', category: 'books', type: 'physical', status: 'borrowed', year: 2021 },
  { id: 3, title: 'Machine Learning Engineering', author: 'Andriy Burkov', rating: 4.9, reviews: 156, description: 'Practical guide to building production-ready ML systems.', category: 'books', type: 'digital', status: 'available', year: 2023 },
  { id: 4, title: 'The Silent Patient', author: 'Alex Michaelides', rating: 4.9, reviews: 512, description: 'A gripping psychological thriller that keeps you guessing until the very end.', category: 'books', type: 'physical', status: 'available', year: 2019 },
  { id: 5, title: 'Atomic Habits', author: 'James Clear', rating: 4.8, reviews: 1024, description: 'Tiny changes, remarkable results. Practical strategies for building good habits.', category: 'books', type: 'physical', status: 'available', year: 2018 },
  { id: 6, title: 'Clean Code', author: 'Robert C. Martin', rating: 4.9, reviews: 890, description: 'Handbook of agile software craftsmanship.', category: 'books', type: 'physical', status: 'available', year: 2020 },
  { id: 7, title: 'Design Patterns', author: 'Erich Gamma', rating: 4.8, reviews: 672, description: 'Elements of reusable object-oriented software.', category: 'books', type: 'physical', status: 'borrowed', year: 2017 },
  { id: 8, title: 'The Pragmatic Programmer', author: 'David Thomas', rating: 4.9, reviews: 734, description: 'Your journey to mastery.', category: 'books', type: 'digital', status: 'available', year: 2019 },
  { id: 9, title: 'National Geographic', author: 'NG Society', rating: 4.6, reviews: 89, description: 'Exploring science, nature, and culture around the world.', category: 'magazine', type: 'digital', status: 'available', year: 2024 },
  { id: 10, title: 'IEEE Spectrum', author: 'IEEE', rating: 4.5, reviews: 67, description: 'Technology insights and innovations shaping our future.', category: 'magazine', type: 'digital', status: 'available', year: 2024 },
  { id: 11, title: 'The Economist', author: 'Economist Group', rating: 4.7, reviews: 112, description: 'Global news, analysis, and economic insights.', category: 'magazine', type: 'physical', status: 'borrowed', year: 2024 },
  { id: 12, title: 'Nature', author: 'Nature Publishing', rating: 4.9, reviews: 234, description: 'Leading scientific journal covering breakthrough research.', category: 'magazine', type: 'digital', status: 'available', year: 2024 },
  { id: 13, title: 'WIRED', author: 'Conde Nast', rating: 4.5, reviews: 78, description: 'How technology is changing our world.', category: 'magazine', type: 'physical', status: 'available', year: 2024 },
  { id: 14, title: 'Machine Learning for Ethiopian Agriculture', author: 'Dr. Bekele T.', rating: 4.8, reviews: 45, description: 'PhD Thesis - Applications of ML in crop yield prediction and agricultural optimization.', category: 'thesis', type: 'digital', status: 'available', year: 2023 },
  { id: 15, title: 'Water Resource Management', author: 'Selam A.', rating: 4.6, reviews: 32, description: 'Masters Thesis - Sustainable water resource management strategies.', category: 'thesis', type: 'digital', status: 'available', year: 2022 },
  { id: 16, title: 'Renewable Energy Integration', author: 'Henok D.', rating: 4.7, reviews: 28, description: 'PhD Thesis - Grid integration strategies for renewable energy.', category: 'thesis', type: 'digital', status: 'borrowed', year: 2023 },
  { id: 17, title: 'NLP for Ethiopian Languages', author: 'Meron T.', rating: 4.9, reviews: 19, description: 'Masters Thesis - Natural language processing for Amharic and Oromo.', category: 'thesis', type: 'digital', status: 'available', year: 2024 },
  { id: 18, title: 'Advanced Research Methods', author: 'Prof. John Creswell', rating: 4.8, reviews: 156, description: 'Comprehensive guide to academic research methodology and design.', category: 'research', type: 'physical', status: 'available', year: 2021 },
  { id: 19, title: 'Quantitative Analysis', author: 'Dr. Sarah Johnson', rating: 4.7, reviews: 98, description: 'Statistical methods for analyzing research data.', category: 'research', type: 'physical', status: 'available', year: 2022 },
  { id: 20, title: 'Qualitative Research Design', author: 'Dr. Robert Yin', rating: 4.9, reviews: 142, description: 'Case study and ethnographic research approaches.', category: 'research', type: 'digital', status: 'available', year: 2020 },
  { id: 21, title: 'Academic Writing Guide', author: 'Prof. Kate Turabian', rating: 4.6, reviews: 87, description: 'Style and formatting for research papers and theses.', category: 'research', type: 'physical', status: 'borrowed', year: 2023 },
  { id: 22, title: 'Mixed Methods Research', author: 'Dr. Michael Fetters', rating: 4.7, reviews: 64, description: 'Integrating qualitative and quantitative approaches.', category: 'research', type: 'digital', status: 'available', year: 2022 }
]);

const filteredMaterials = computed(() => {
  let filtered = allMaterials.value.filter(m => m.category === selectedCategory.value);
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(m => 
      m.title.toLowerCase().includes(query) || 
      m.author.toLowerCase().includes(query)
    );
  }
  return filtered;
});

const sortedMaterials = computed(() => {
  const items = [...filteredMaterials.value];
  switch (sortBy.value) {
    case 'newest': return items.sort((a, b) => b.year - a.year);
    case 'oldest': return items.sort((a, b) => a.year - b.year);
    case 'title': return items.sort((a, b) => a.title.localeCompare(b.title));
    case 'rating': return items.sort((a, b) => b.rating - a.rating);
    default: return items;
  }
});

function getCategoryLabel(category) {
  const labels = { books: 'Books', magazine: 'Magazines', thesis: 'Theses', research: 'Research Books' };
  return labels[category] || 'Materials';
}

// Staff Data
const staffMembers = ref([
  { id: 1, name: 'Tewelgn Kebede (PhD)', role: 'Director of Hawassa University Library', bio: 'Tewelgn Kebede, based in Addis Ababa, ET, is currently a Director, Library Services at Hawassa University. Tewelgn Kebede brings experience from previous roles at Hawassa University, UNite Nations Development Program-United Nations Volunteer (UNDP-UNV) ICT Specia and SNNP Region Capacity Building Bureau. Tewelgn Kebede holds a 2018 - 2022 Doctor of Philosophy - PhD in Communication Engineering @ Addis Ababa University, Ethiopia and Kempten University of Applied Sciences, Germany.', email: 'library@hu.edu.et', experience: 'highly experienced', image: tewl },
]);
const staffIndex = ref(0);
let staffInterval;

function prevStaff() {
  staffIndex.value = (staffIndex.value - 1 + staffMembers.value.length) % staffMembers.value.length;
}
function nextStaff() {
  staffIndex.value = (staffIndex.value + 1) % staffMembers.value.length;
}

// FAQs
const faqs = ref([
  { q: 'Do I need to login to browse materials?', a: 'No, you can browse all materials and see availability without logging in. However, you need to sign in to borrow physical books or read digital resources.' },
  { q: 'How long can I borrow a book?', a: 'Standard borrowing period is 14 days for undergraduate students and 30 days for graduate students and faculty.' },
  { q: 'How do I access digital resources?', a: 'Digital resources can be accessed immediately after signing in. You can read online or download (where permitted) based on your account type.' },
  { q: 'What if the book I want is borrowed?', a: 'You can reserve the book and you will be notified via email when it becomes available.' }
]);

const openFaq = ref(null);
const showLoginPrompt = ref(false);
const showHelpModal = ref(false);
const pendingAction = ref('');
const pendingItemTitle = ref('');

function viewLibraryCollections(library) {
  router.push(`/app/materials?library=${encodeURIComponent(library.name)}`);
}

function getBookImage(title, category) {
  const imageMap = {
    'Introduction to Algorithms': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop',
    'Database Systems': 'https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=300&h=400&fit=crop',
    'Machine Learning Engineering': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=300&h=400&fit=crop',
    'The Silent Patient': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop',
    'Atomic Habits': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop',
    'Clean Code': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=300&h=400&fit=crop',
    'Design Patterns': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=300&h=400&fit=crop',
    'The Pragmatic Programmer': 'https://images.unsplash.com/photo-1580894908361-967195033215?w=300&h=400&fit=crop',
    'National Geographic': 'https://images.unsplash.com/photo-1586339949916-3e9457bef6d3?w=300&h=400&fit=crop',
    'IEEE Spectrum': 'https://images.unsplash.com/photo-1509023464722-18d996393ca8?w=300&h=400&fit=crop',
    'The Economist': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop',
    'Nature': 'https://images.unsplash.com/photo-1578301978693-85fa9c0320b9?w=300&h=400&fit=crop',
    'WIRED': 'https://images.unsplash.com/photo-1550399105-c4db5fb85c18?w=300&h=400&fit=crop',
    'Machine Learning for Ethiopian Agriculture': 'https://images.unsplash.com/photo-1598257006626-48b0c252070d?w=300&h=400&fit=crop',
    'Water Resource Management': 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=300&h=400&fit=crop',
    'Renewable Energy Integration': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=300&h=400&fit=crop',
    'NLP for Ethiopian Languages': 'https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=300&h=400&fit=crop',
    'Advanced Research Methods': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop',
    'Quantitative Analysis': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300&h=400&fit=crop',
    'Qualitative Research Design': 'https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=300&h=400&fit=crop',
    'Academic Writing Guide': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300&h=400&fit=crop',
    'Mixed Methods Research': 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=300&h=400&fit=crop'
  };
  if (imageMap[title]) return imageMap[title];
  const categoryImages = {
    books: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop',
    magazine: 'https://images.unsplash.com/photo-1586339949916-3e9457bef6d3?w=300&h=400&fit=crop',
    thesis: 'https://images.unsplash.com/photo-1598257006626-48b0c252070d?w=300&h=400&fit=crop',
    research: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=400&fit=crop'
  };
  return categoryImages[category] || 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop';
}

function handleAction(action, title) {
  pendingAction.value = action;
  pendingItemTitle.value = title;
  showLoginPrompt.value = true;
}

function scrollTo(sectionId) {
  mobileMenuOpen.value = false;
  const element = document.getElementById(sectionId);
  if (element) element.scrollIntoView({ behavior: 'smooth' });
}

onMounted(() => {
  slideshowInterval = setInterval(() => {
    currentSlide.value = (currentSlide.value + 1) % heroSlides.value.length;
  }, 5000);
  selectCampus(campuses.value[0]);
  staffInterval = setInterval(() => {
    staffIndex.value = (staffIndex.value + 1) % staffMembers.value.length;
  }, 8000);
});

onUnmounted(() => {
  if (slideshowInterval) clearInterval(slideshowInterval);
  if (libraryInterval) clearInterval(libraryInterval);
  if (staffInterval) clearInterval(staffInterval);
});
</script>

<style scoped>
/* Mobile Menu Transition */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.3s ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.mobile-menu-enter-to,
.mobile-menu-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* FAQ Expand/Collapse */
.faq-expand-enter-active,
.faq-expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.faq-expand-enter-from,
.faq-expand-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-8px);
}
.faq-expand-enter-to,
.faq-expand-leave-from {
  opacity: 1;
  max-height: 200px;
  transform: translateY(0);
}

/* Slide Text Animation */
.slide-text-enter-active,
.slide-text-leave-active {
  transition: all 0.5s ease;
}
.slide-text-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.slide-text-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Campus and Library Transitions */
.campus-fade-enter-active,
.campus-fade-leave-active,
.library-fade-enter-active,
.library-fade-leave-active {
  transition: all 0.4s ease;
}
.campus-fade-enter-from,
.campus-fade-leave-to,
.library-fade-enter-from,
.library-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
.campus-fade-enter-to,
.campus-fade-leave-from,
.library-fade-enter-to,
.library-fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* FAQ Item Hover */
.faq-item:hover {
  background: rgba(0, 0, 0, 0.02);
}
:is(.dark) .faq-item:hover {
  background: rgba(255, 255, 255, 0.02);
}
</style>