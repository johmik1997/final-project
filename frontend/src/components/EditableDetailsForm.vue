<template>
  <div class="p-4">
    <!-- Client Info Section -->
    <div class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Client Info</h2>
        <button 
          v-if="!isEditingClient" 
          @click="toggleClientEdit"
          class="text-primary hover:text-primary-dark"
        >
          <i class="fas fa-edit"></i> Edit
        </button>
      </div>

      <div v-if="!isEditingClient" class="grid grid-cols-2 gap-4">
        <div class="text-gray-600">First Name</div>
        <div>{{ clientData.firstName }}</div>
        
        <div class="text-gray-600">Last Name</div>
        <div>{{ clientData.lastName }}</div>
        
        <div class="text-gray-600">Email</div>
        <div>{{ clientData.email }}</div>
        
        <div class="text-gray-600">Phone Number</div>
        <div>{{ clientData.phoneNumber }}</div>
      </div>

      <form v-else class="grid grid-cols-2 gap-4">
        <div class="text-gray-600">First Name</div>
        <input v-model="editedClientData.firstName" class="border rounded p-1" />
        
        <div class="text-gray-600">Last Name</div>
        <input v-model="editedClientData.lastName" class="border rounded p-1" />
        
        <div class="text-gray-600">Email</div>
        <input v-model="editedClientData.email" class="border rounded p-1" />
        
        <div class="text-gray-600">Phone Number</div>
        <input v-model="editedClientData.phoneNumber" class="border rounded p-1" />
      </form>
    </div>

    <!-- Vehicle Details Section -->
    <div>
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">Vehicle Details</h2>
        <button 
          v-if="!isEditingVehicle" 
          @click="toggleVehicleEdit"
          class="text-primary hover:text-primary-dark"
        >
          <i class="fas fa-edit"></i> Edit
        </button>
      </div>

      <div v-if="!isEditingVehicle" class="grid grid-cols-2 gap-4">
        <div class="text-gray-600">Vehicle Make</div>
        <div>{{ vehicleData.carName }}</div>
        
        <div class="text-gray-600">Vehicle Model</div>
        <div>{{ vehicleData.carModel }}</div>
        
        <div class="text-gray-600">Vehicle Year</div>
        <div>{{ vehicleData.makeYear }}</div>
        
        <div class="text-gray-600">Plate Code</div>
        <div>{{ vehicleData.plateNumber }}</div>
        
        <div class="text-gray-600">Category One</div>
        <div>{{ vehicleData.rateRequest.category1 }}</div>
        
        <div class="text-gray-600">Category Two</div>
        <div>{{ vehicleData.rateRequest.category2 }}</div>
        
        <div class="text-gray-600">Category Three</div>
        <div>{{ vehicleData.rateRequest.category3 }}</div>
        
        <div class="text-gray-600">Category Four</div>
        <div>{{ vehicleData.rateRequest.category4 }}</div>
      </div>

      <form v-else class="grid grid-cols-2 gap-4">
        <div class="text-gray-600">Vehicle Make</div>
        <input v-model="editedVehicleData.carName" class="border rounded p-1" />
        
        <div class="text-gray-600">Vehicle Model</div>
        <input v-model="editedVehicleData.carModel" class="border rounded p-1" />
        
        <div class="text-gray-600">Vehicle Year</div>
        <input v-model="editedVehicleData.makeYear" class="border rounded p-1" />
        
        <div class="text-gray-600">Plate Code</div>
        <input v-model="editedVehicleData.plateNumber" class="border rounded p-1" />
        
        <div class="text-gray-600">Category One</div>
        <input v-model="editedVehicleData.rateRequest.category1" class="border rounded p-1" />
        
        <div class="text-gray-600">Category Two</div>
        <input v-model="editedVehicleData.rateRequest.category2" class="border rounded p-1" />
        
        <div class="text-gray-600">Category Three</div>
        <input v-model="editedVehicleData.rateRequest.category3" class="border rounded p-1" />
        
        <div class="text-gray-600">Category Four</div>
        <input v-model="editedVehicleData.rateRequest.category4" class="border rounded p-1" />
      </form>

      <div v-if="isEditingVehicle || isEditingClient" class="mt-4 flex justify-end">
        <button 
          @click="cancelEdit" 
          class="mr-2 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          Cancel
        </button>
        <button 
          @click="saveChanges" 
          class="px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark"
        >
          Save Changes
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';

const props = defineProps({
  clientData: {
    type: Object,
    required: true
  },
  vehicleData: {
    type: Object,
    required: true
  },
  carUuid: {
    type: String,
    required: true
  }
});

const isEditingClient = ref(false);
const isEditingVehicle = ref(false);

const editedClientData = reactive({ ...props.clientData });
const editedVehicleData = reactive({
  ...props.vehicleData,
  rateRequest: { ...props.vehicleData.rateRequest }
});

const toggleClientEdit = () => {
  isEditingClient.value = true;
};

const toggleVehicleEdit = () => {
  isEditingVehicle.value = true;
};

const cancelEdit = () => {
  isEditingClient.value = false;
  isEditingVehicle.value = false;
  Object.assign(editedClientData, props.clientData);
  Object.assign(editedVehicleData, props.vehicleData);
};

const saveChanges = async () => {
  try {
    const response = await axios.put(
      `http://192.168.100.85:8989/api/premium/cars/updateCar/${props.carUuid}`,
      {
        rateRequest: {
          category1: editedVehicleData.rateRequest.category1,
          category2: editedVehicleData.rateRequest.category2,
          category3: editedVehicleData.rateRequest.category3,
          category4: editedVehicleData.rateRequest.category4
        },
        carName: editedVehicleData.carName,
        carModel: editedVehicleData.carModel,
        carType: editedVehicleData.carType,
        plateNumber: editedVehicleData.plateNumber,
        makeYear: editedVehicleData.makeYear,
        buyingPrice: editedVehicleData.buyingPrice || 0
      }
    );

    if (response.data.success) {
      isEditingClient.value = false;
      isEditingVehicle.value = false;
      // Emit success event
      emit('update:success');
    }
  } catch (error) {
    console.error('Error updating car details:', error);
    // Handle error (show toast notification, etc.)
  }
};
</script>