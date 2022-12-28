

def validate_integer(value):
    try:
        value = int(value)
    except ValueError:
        value = False
    return value


def get_true_fruit_name(name, count):
    fruits = {"Яблоки": {1: "яблоко",
                         2: "яблока",
                         3: "яблока",
                         4: "яблока",
                         5: "яблок",
                         'english': 'apple'
                         },
              "Ананасы": {
                         1: "ананасов",
                         2: "ананаса",
                         3: "ананаса",
                         4: "ананаса",
                         5: "ананасов",
                         'english': 'pineapple'
              },
              "Бананы": {
                         1: "бананов",
                         2: "банана",
                         3: "банана",
                         4: "банана",
                         5: "бананов",
                         'english': 'banana'

              },
              "Апельсины": {
                  1: "апельсин",
                  2: "апельсина",
                  3: "апельсина",
                  4: "апельсина",
                  5: "апельсинов",
                  'english': 'orange'

              },
              "Абрикосы": {
                  1: "абрикоса",
                  2: "абрикосы",
                  3: "абрикосы",
                  4: "абрикосы",
                  5: "абрикос",
                  'english': 'apricot'

              },
              "Киви": {
                  1: "киви",
                  2: "киви",
                  3: "киви",
                  4: "киви",
                  5: "киви",
                  'english': 'kiwi'
              },
        }
    true_name = fruits[name][count] if count == "english" or count <= 4 else fruits[name][5]
    return true_name
