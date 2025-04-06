const VALID_MOVEMENTS = ['Yuko', 'Wazari', 'Wazaari Awasete', 'Toketa', 'Sonomama', 'Osaekomi', 'Matte', 'Koka', 'Ippon', 'Hantei', 'Hajime']

document.addEventListener('alpine:init', () => {

  Alpine.store('movements', {
    data: [],

    add(new_movement) {
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
