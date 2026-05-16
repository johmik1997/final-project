import { faker } from '@faker-js/faker'

export async function getAllAgenncies() {
  const agencies = []
  for(let i = 0; i < 10; i++) {
    const agency = {}
    agencies.id = faker.datatype.uuid
    agencies.name = faker.company.name
  }
  return agencies
}