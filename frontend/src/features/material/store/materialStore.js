import { ref } from "vue"
import { defineStore } from "pinia"

export const useMaterials = defineStore("materialsStore", () => {

  const materials = ref([])
  const createType = ref("physical")

  function set(data){
    materials.value = data
  }

  function add(data){
    materials.value.push(data)
  }

  function getAll() {
    return materials.value
  }

  function setCreateType(type) {
    createType.value = String(type || "physical").toLowerCase() === "digital" ? "digital" : "physical"
  }

  function getMaterialId(material){
    return material?.uuid || material?.materialUuid || material?.id
  }

  function update(id,data){
    const idx = materials.value.findIndex(el => getMaterialId(el) == id)
    if(idx === -1) return
    materials.value.splice(idx,1,data)
  }

  function remove(id){
    const idx = materials.value.findIndex(el => getMaterialId(el) == id)
    if(idx === -1) return
    materials.value.splice(idx,1)
  }

  return {
    materials,
    getAll,
    createType,
    setCreateType,
    set,
    add,
    update,
    remove
  }

})
