/**
 * Миксин Vue для работы с каталогом товаров
 * 
 * @typedef {Object} Tag
 * @property {number} id - Идентификатор тега
 * @property {string} name - Название тега
 * @property {boolean} selected - Состояние выбора тега
 * 
 * @typedef {Object} SortRule
 * @property {string} id - Идентификатор правила сортировки
 * @property {string} title - Название правила сортировки
 * @property {'inc'|'dec'} selected - Направление сортировки
 * 
 * @typedef {Object} Filter
 * @property {string} name - Фильтр по названию
 * @property {number} minPrice - Минимальная цена
 * @property {number} maxPrice - Максимальная цена
 * @property {boolean} freeDelivery - Фильтр по бесплатной доставке
 * @property {boolean} available - Фильтр по наличию
 * 
 * @typedef {Object} ProductCard
 * @property {number} id - Идентификатор продукта
 * @property {string} title - Название продукта
 * @property {number} price - Цена продукта
 * @property {Array<{src: string, alt: string}>} images - Изображения продукта
 * 
 * @typedef {Object} CatalogResponse
 * @property {Array<ProductCard>} items - Список товаров
 * @property {number} currentPage - Текущая страница
 * @property {number} lastPage - Последняя страница
 * @property {number} total - Общее количество товаров
 */

/**
 * Глобальный миксин для компонента каталога
 * @type {import('vue').ComponentOptions}
 */
var mix = {
    /**
     * Методы компонента
     * @type {Object<string, Function>}
     */
    methods: {
        /**
         * Переключает состояние выбранного тега
         * @param {number} id - Идентификатор тега
         * @returns {void}
         */
        setTag(id) {
            // Обновляем состояние тегов
            this.topTags = this.topTags.map(tag => {
                return tag.id === id
                    ? {
                        ...tag,
                        selected: !tag.selected
                    }
                    : tag
            });
            // Загружаем каталог с новыми фильтрами
            this.getCatalogs(1);
        },

        /**
         * Устанавливает правило сортировки
         * @param {string} id - Идентификатор правила сортировки
         * @returns {void}
         */
        setSort(id) {
            if (this.selectedSort?.id === id) {
                // Меняем направление сортировки
                this.selectedSort.selected =
                    this.selectedSort.selected === 'dec'
                        ? 'inc'
                        : 'dec';
            } else {
                // Устанавливаем новое правило сортировки
                this.selectedSort = this.sortRules.find(sort => sort.id === id);
                this.selectedSort = {
                    ...this.selectedSort,
                    selected: 'dec'
                };
            }
            // Загружаем каталог с новой сортировкой
            this.getCatalogs(1);
        },

        /**
         * Получает список тегов с сервера
         * @returns {void}
         */
        getTags() {
        console.log('Запрашиваем теги...');
        this.getData('/api/tags')
            .then(data => {
            // Очищаем и добавляем элементы по одному — это гарантирует реактивность
            this.topTags = [];
            const mapped = data.map(tag => ({
                ...tag,
                selected: false
            }));
            // Полная замена — в Vue 3 это реактивно при использовании обычного присваивания
            this.topTags = mapped;
            })
            .catch(() => {
            this.topTags = [];
            console.warn('Ошибка получения тегов');
            });
        },

        /**
         * Получает список товаров с сервера
         * @param {number} [page=1] - Номер страницы
         * @returns {void}
         */
        getCatalogs(page = 1) {
            const PAGE_LIMIT = 20;
            
            // Фильтруем выбранные теги
            const selectedTags = this.topTags
                .filter(tag => !!tag.selected)
                .map(tag => tag.id);
            
            // Формируем параметры запроса
            const params = {
                filter: this.filter.name || '',
                minPrice: this.filter.minPrice || 0,
                maxPrice: this.filter.maxPrice || 50000,
                available: this.filter.available,
                freeDelivery: this.filter.freeDelivery,
                category: this.category,
                sort: this.selectedSort ? this.selectedSort.id : 'date',
                sortType: this.selectedSort ? this.selectedSort.selected : 'dec',
                limit: PAGE_LIMIT,
                page: page
            };

            // Убираем undefined параметры
            Object.keys(params).forEach(key => {
                if (params[key] === undefined) {
                    delete params[key];
                }
            });

            // Отправляем POST запрос к API каталога
            this.postData("/api/catalog/", params)
                .then(response => {
                    const data = response.data;
                    // Обновляем данные компонента
                    this.catalogCards = data.items || [];
                    this.currentPage = data.currentPage || 1;
                    this.lastPage = data.lastPage || 1;
                })
                .catch(error => {
                    console.warn('Ошибка при получении каталога:', error);
                    this.catalogCards = [];
                    this.currentPage = 1;
                    this.lastPage = 1;
                });
        }
    },

    /**
     * Выполняется после монтирования компонента
     * @returns {void}
     */
    mounted() {
        // Инициализируем правила сортировки при необходимости
        if (!this.sortRules) {
            this.sortRules = [
                { id: 'price', title: 'Цене' },
                { id: 'rating', title: 'Рейтингу' },
                { id: 'reviews', title: 'Популярности' },
                { id: 'date', title: 'Дате' }
            ];
        }

        // Устанавливаем правило сортировки по умолчанию
        this.selectedSort = this.sortRules[0]
            ? { ...this.sortRules[0], selected: 'dec' }
            : { id: 'date', title: 'Дате', selected: 'dec' };

        // Определяем категорию из URL
        if(location.pathname.startsWith('/catalog/')) {
            const category = location.pathname.replace('/catalog/', '').replace('/', '');
            this.category = category.length ? Number(category) : null;
        }

        // Загружаем данные
        this.getCatalogs(1);
        this.getTags();
    },

    /**
     * Инициализация данных компонента
     * @returns {Object} Объект с данными компонента
     */
    data() {
        return {
            /** @type {number|null} - Идентификатор категории */
            category: null,
            
            /** @type {Array<ProductCard>} - Список карточек товаров */
            catalogCards: [],
            
            /** @type {number} - Текущая страница */
            currentPage: 1,
            
            /** @type {number} - Последняя страница */
            lastPage: 1,
            
            /** @type {SortRule|null} - Выбранное правило сортировки */
            selectedSort: null,
            
            /** @type {Filter} - Параметры фильтрации */
            filter: {
                name: '',
                minPrice: 0,
                maxPrice: 50000,
                freeDelivery: false,
                available: true
            },
            
            /** @type {Array<Tag>} - Список тегов */
            topTags: [],
            
            /** @type {Array<SortRule>} - Правила сортировки */
            sortRules: [
                { id: 'price', title: 'Цене' },
                { id: 'rating', title: 'Рейтингу' },
                { id: 'reviews', title: 'Популярности' },
                { id: 'date', title: 'Дате' }
            ],
            
            /** @type {Object} - Дополнительные фильтры */
            filters: {
                price: {
                    minValue: 0,
                    maxValue: 50000
                }
            }
        };
    }
};
