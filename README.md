# turtle-3d
A simple repository with 3D rendering using standard python turtle library. Can be used to draw complex shapes, though, obviously, insanely slow.

## An example
A House by **Poly by Google** [CC-BY](https://creativecommons.org/licenses/by/3.0/) via [Poly Pizza](https://poly.pizza/m/75V_MLvKMqM)

![house](https://github.com/user-attachments/assets/ab16449c-6733-48e9-89dc-2d0a405a7b43)

A Boat by **Poly by Google** [CC-BY](https://creativecommons.org/licenses/by/3.0/) via [Poly Pizza](https://poly.pizza/m/1ZuSXvhkRg_)

![boat](https://github.com/user-attachments/assets/3ca5f5e1-0d5d-41b7-b2e0-07ffd8cf1542)

## How to use
### Model
To load your custom model, simply change the constant `MODEL` to your custom model's path (This project only supports .obj models)
```py
MODEL = "mymodel.obj"
```

### Size
To change size, you have to play with the `SIZE` costant. I'm quite lazy, so I won't implement a separate control for this.
The lower the setting - the smaller the model, and vice-versa.
### Controls
To change rotation speed, use arrow keys:
- Left to reduce the rotation speed
- Right to increase the rotation speed
- Up to rotate the model on x axis by 5 degrees
- Down to rotate the model on x axis by -5 degrees

### Dynamic

By setting
```py
DYNAMIC = True
```

you will be able to see turtle movements in real time. This however will be very slow, and not recommended if you just want to see the frames as they are.
