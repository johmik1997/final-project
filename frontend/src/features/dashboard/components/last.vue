<template>  
    <div class="flex bg-white space-x-4 p-4">  
      <!-- Card 1 -->  
      <div class=" p-4 w-1/3">  
        <div class="flex items-center space-x-2">  
          <div class="p-2">  
           <i v-html="icons.fire" class=""></i>
          </div>  
          <div class="text-gray-600 text-sm">Business</div>  
        </div>  
        <h2 class="font-bold mt-2">New session is available</h2>  
        <p class="mt-2 text-gray-800">  
          What do you need to know to create better products?  
        </p>  
        <div class="flex items-center justify-between mt-4">  
          <span class="text-green-600 font-semibold">85 mins</span>  
          <span class="text-red-500 font-semibold">Video format</span>  
        </div>  
        <div class="flex items-center justify-between mt-4">  
         <div>
             <i v-html="icons.avatars" class=""></i>
         <!-- <i v-html="icons.avatar2" class=""></i>
         <i v-html="icons.avatar3" class=""></i> -->
           <!-- <span class="ml-1 text-gray-600">18+</span>  -->
         </div>
          <button class=" bg-[#4318FF] text-white py-2 px-2 rounded-full hover:bg-[#462db3]">  
          Get Started  
        </button>  
        </div>  
      
      </div>  
  
      <!-- Card 2 -->  
      <div class=" p-4 w-1/3">  
        <div class="flex items-center justify-between">
            <h2 class="font-bold">Team members</h2>  
            <i v-html="icons.adds" class=""></i> 
        </div>
        <div class="mt-3  bg-[#7090B01F]">  
          <div class="flex rounded-xl bg-white items-center justify-between py-2">  
            <div class="flex">
                <i v-html="icons.avatar1" class="pr-2"></i>  
                <div> 
                    <span class="font-semibold">Adela Parkson</span>  
                    <p class="text-gray-600 text-sm">Creative Director</p>  
                </div>
            </div>  
            <button class="text-gray-400 mr-3">⋮</button>  
          </div>  
          <div class="flex rounded-xl items-center bg-white mt-2  justify-between py-2">  
            <div class="flex">
                <i v-html="icons.avatar2" class="pr-2"></i>  
                <div>  
              <span class="font-semibold">Christian Mad</span>  
              <p class="text-gray-600 text-sm">Product Designer </p>  
            </div>
            </div>  
            <button class="text-gray-400 mr-3">⋮</button>  
          </div>  
          <div class="flex rounded-xl items-center bg-white mt-2 justify-between py-2">  
            <div class="flex">
                <i v-html="icons.avatar3" class="pr-2"></i>  
                <div>  
              <span class="font-semibold">Jason Statham</span>  
              <p class="text-gray-600 text-sm">Junior Graphic Designer</p>  
            </div>
            </div>  
            <button class="text-gray-400 mr-3">⋮</button>  
          </div>  
        </div>  
       
      </div>  
  
      <!-- Card 3 -->  
      <div class=" p-4 w-1/3">  
        <i v-html="icons.fingerPrint" class=""></i>
        <h2 class="font-bold">Control card security in-app with a tap</h2>  
        <p class="mt-2 text-gray-600">Discover our cards benefits, with one tap.</p>  
        <button class="w-full bg-purple-600 text-white py-2 rounded mt-4 hover:bg-purple-500">  
          Cards  
        </button>  
      </div>  
    </div>  
  </template>  
  
  <script setup>
import icons from '@/utils/icons';

  
  /* You can add any necessary imports or logic here if needed */  
  </script>  
  
  <style scoped>  
  /* You can add additional styles here */  
  </style>