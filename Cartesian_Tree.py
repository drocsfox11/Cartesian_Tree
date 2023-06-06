from PIL import ImageDraw, Image, ImageFont
from random import randint


class TreeElement:
    def __init__(self, value: int, priority: int):
        """
        Класс описывает элементы декартового дерева Treap
        self.right: ссылка на правое поддерево данного элемента
        self.left: ссылка на левое поддерево данного элемента
        :param value: Значение веришины (координата X для рисования), используется для формирования дерева поиска
        :param priority: Приоритет вершины (координата Y для рисования), используется для формирования кучи
        """
        self.value: int = value
        self.left: TreeElement | None = None
        self.right: TreeElement | None = None
        self.priority: int = priority

    def __str__(self):
        return str(self.value)


class Treap:
    """
    Класс реализующий работу декартового дерева.
    В качестве элементов дерева выступают объекты класса TreeElement

    _CIRCLE_RADIUS: Размер вершин в отрисовке дерева (Treap._paint)
    _FONT: Шрифт, используемый в отрисовке дерева (Treap._paint)
    _SCALE: Увеличение изображения в отрисовке дерева (Treap._paint). - Необходимо,
    из-за того что рисование производится по координатам элементов, а они зачастую очень малы
    """

    _CIRCLE_RADIUS = 20
    _FONT = ImageFont.truetype("arial.ttf", 20)
    _SCALE = 30

    def __init__(self):
        """
        self.root: ссылка на самый верхний элемент декартового дерева
        """
        self.root: TreeElement | None = None

    @staticmethod
    def split(treap: TreeElement, split_value: int) -> (TreeElement | None, TreeElement | None):
        """
        Функция делит правильное декартово дерево на два других Декартовых дерево, большее split_value
        и меньшее split_value
        :param treap: Дерево которое будем разделять
        :param split_value: Значение по которому будем разделять данное дерево
        :return: Если дерево не пустое (None), то первое значение это меньшее дерево, а второе - большее
        """

        if treap is None:
            # Пустое дерево можно разделить только на два пустых
            return None, None

        if treap.value < split_value:
            # Если вершина разделяемого дерева меньше значения для разделения
            # делим правую часть этого дерева на элементы большие split_value, и меньшие
            # меньшие прицепляем направо к исходному дереву, в большие возвращаем как дерево большее
            # чем split_value
            lower_than_split_value, bigger_than_split_value = Treap.split(treap.right, split_value)
            treap.right = lower_than_split_value
            return treap, bigger_than_split_value
        else:
            # Зеркальный случай
            # Оставляем без изменений вершину дерева и ее правую часть
            # левую часть делим на элементы меньшие split_value< и большие
            # большие цепляем к исходному дереву налево, а меньшие возвращаем в качестве меньшего дерева
            lower_than_split_value, bigger_than_split_value = Treap.split(treap.left, split_value)
            treap.left = bigger_than_split_value
            return lower_than_split_value, treap

    @staticmethod
    def merge(left_treap: TreeElement, right_treap: TreeElement) -> TreeElement:
        """
        Функция склеивает два входных декартовых дерева.
        ВАЖНО!
        left_treap полностью меньше right_treap
        :param left_treap: Меньшее дерево
        :param right_treap: Большее дерево
        :return: Склееное дерево
        """

        # При склеивании любого дерева с пустым, оно не меняется
        if left_treap is None:
            return right_treap
        if right_treap is None:
            return left_treap

        if left_treap.priority > right_treap.priority:
            # Если приоритет левого дерева больше, то его вершина станет корневой для этих двух деревьев,
            # Правое дерево (right_treap) прицепится к корневому элементу направо,
            # но тогда мы потеряем left_treap.right ,чтобы этого не произошло нам нужно слить
            # left_treap.right с right_treap, мы можем это сделать т.к. left_treap полностью меньше right_treapб
            # а значит left_treap.right полностью меньше right_treap
            left_treap.right = Treap.merge(left_treap.right, right_treap)
            return left_treap

        else:
            # Ситуация зеркальна первому случаю
            # правое дерево (right_treap) становится корнем, подвешиваем у нему налево left_treap,
            # и чтобы right_treap.left не исчезло, сливаем его с left_treap
            right_treap.left = Treap.merge(left_treap, right_treap.left)
            return right_treap

    def add(self, value: int, priority: int) -> None:
        """
        Метод делит дерево на два поддерева, меньшее добавляемого элемента, и большее добавляемого элемента,
        а после склеивает в порядке:
        1) промежуточный результат = (меньшее, элемент)
        2) (промежуточный результат, большее)
        (Склеивание в таком порядке из-за особенности работы функции merge)
        В конце, сохраняем полученный результат в self.root
        :param value: Значение добавляемого элемента (X координата)
        :param priority: Приоритет добавляемого элемента (Y координата)
        :return: None
        """

        new_element = TreeElement(value, priority)
        left_treap, right_treap = self.split(self.root, value)
        self.root = self.merge(self.merge(left_treap, new_element), right_treap)

    def find(self, current_root: TreeElement, value: int) -> (TreeElement, str):
        """
        Фукнция находит предка узла со значением value среди поддеревьев этого узла
        :param current_root: текущий узел
        :param value: значение искомого узла
        :return: родитель искомого узла и сторона с которой находится искомый узел
        """

        if current_root.left is not None:
            # Если искомый узел в левом потомке, возвращаем его
            if current_root.left.value == value:
                return current_root, 'L'
        if current_root.right is not None:
            # Если искомый узел в правом потомке, возвращаем его
            if current_root.right.value == value:
                return current_root, 'R'

        # Если дошлю сюда, значит ответ не среди первых потомков этого узла
        # Тогда продолжаем поиск как в дереве поиска:
        # Если значение искомого узла меньше значения текущей вершины ищем слева
        # Иначе ищем справа
        if value < current_root.value:
            return self.find(current_root.left, value)
        return self.find(current_root.right, value)

    def remove(self, value) -> None:
        """
        Метод удаляет узел со значением value из дерева
        :param value: значение удаляемого узла
        :return: None
        """

        # находим предка удяляемого узла и сторону с которой он находится
        prev, side = self.find(self.root, value)

        # заменяем удаляемый узел на результат склеивания его левого и правого потомков
        #  в зависимости от side, удаляемый узел будет лежать в:
        #  1) 'L' -> prev.left
        #  2) 'R' -> prev.right
        if side == 'L':
            prev.left = self.merge(prev.left.left, prev.left.right)
        else:
            prev.right = self.merge(prev.right.left, prev.right.right)

    def paint(self, draw_instrument: ImageDraw.Draw, height: int) -> None:
        """
        Рисует данное декартово дерево начиная с корня
        :param draw_instrument: Инструмент рисования
        :param height: Высота картинки
        :return: None
        """

        self._paint(self.root, draw_instrument, height)

    @classmethod
    def _paint(cls, root: TreeElement, draw_instrument: ImageDraw.Draw, height: int) -> None:
        """
        Метод отрисовывает текущий элемент, его значение, и ветви до дочерних элементов, если они есть,
        а после рекурсивно вызывается от дочерних элементов
        :param root: Текущий элемент
        :param draw_instrument:  Инструмент отрисовки, привязанный к изображению
        :param height: Высота изображения, нужна чтобы вершины рисовались сверху вниз, а не наоборот,
        из-за того, что в pillow отсчет координаты Y идет сверху вниз.
        """
        x, y = root.value * cls._SCALE, height - root.priority * cls._SCALE
        if root.left:
            # Рисуем ветвь до левого дочернего элемента
            draw_instrument.line([x, y, root.left.value * cls._SCALE, height - root.left.priority * cls._SCALE],
                                 'black')
            # Рисуем дерево от левого дочернего элемента
            cls._paint(root.left, draw_instrument, height)
        if root.right:
            # Рисуем ветвь до правого дочернего элемента
            draw_instrument.line([x, y, root.right.value * cls._SCALE, height - root.right.priority * cls._SCALE],
                                 'black')
            # Рисуем дерево от правого дочернего элемента
            cls._paint(root.right, draw_instrument, height)

        # Рисуем текущую вершину
        draw_instrument.ellipse(
            [x - cls._CIRCLE_RADIUS, y - cls._CIRCLE_RADIUS, x + cls._CIRCLE_RADIUS,
             y + cls._CIRCLE_RADIUS], outline='black')
        draw_instrument.text((x - cls._CIRCLE_RADIUS, y - cls._CIRCLE_RADIUS * 2),
                             f'{root.value}, {root.priority}',
                             'black', font=cls._FONT)


width, height = 1000, 1000
img = Image.new('RGB', (width, height), 'white')
draw = ImageDraw.Draw(img)

tr = Treap()

for i in range(20):
    tr.add(randint(0, 30), randint(0, 30))

tr.paint(draw, 1000)
img.show()

n = int(input())
tr.remove(n)

img2 = Image.new('RGB', (width, height), 'white')
draw2 = ImageDraw.Draw(img2)

tr.paint(draw2, 1000)
img2.show()
