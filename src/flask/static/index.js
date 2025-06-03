
document.addEventListener('alpine:init', () => {

  Alpine.store('movements', {
    data: [],
    // valid: ['Yuko', 'Wazari', 'Wazaari Awasete', 'Toketa', 'Sonomama', 'Osaekomi', 'Matte', 'Koka', 'Ippon', 'Hantei', 'Hajime'],
    valid: ['Ippon', 'Matte', 'Wazari', 'ScoreChange', 'Toketa', 'Toketa'],


    addRandom() {
      const VALID_MOVEMENTS = this.valid
      const movement = VALID_MOVEMENTS[Math.floor(Math.random() * VALID_MOVEMENTS.length)]

      this.add(movement)
    },

    add(new_movement) {
      const VALID_MOVEMENTS = this.valid
      const movement_list = this.data

      if (movement_list.length > 10) {
        movement_list.shift();
      }

      for (let [i, item] of Object.entries(movement_list)) {
        item.current = false
        item.index = i
      }

      const index = movement_list.length ? movement_list.length : 0
      const key = movement_list.length ? movement_list.at(-1).key + 1 : 0
      const image = VALID_MOVEMENTS.includes(new_movement) ? `/static/images/${new_movement}.png` : ''

      movement_list.push({
        name: new_movement,
        image: image,
        current: true,
        key: key,
        index: index,
      })
    }
  })

})
