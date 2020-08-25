Vue.use(vuescroll);

var cotoprices = new Vue({
    el: '#cotoprices',
    components: {
        vuejsDatepicker
    },
    data: {
        prices: [],
        filterDate: dayjs().format("YYYY-MM-DD"),
        ops: {
            rail: {
                opacity: '0.2',
                background: '#F92672',
                border: '0px',
                size: '6px'
            },
            bar: {
                background: '#f7f1f1',
                keepShow: false,
                size: '6px',
                minSize: 0.2
            },
            scrollButton: {
                enable: false,
                background: '#cecece'
            },
            scrollPanel: {
                easing: 'easeInQuad',
                speed: 800
            },
            vuescroll: {
                wheelScrollDuration: 0,
                wheelDirectionReverse: false
            }
        },
        datepicker: {
            date: dayjs().toDate(),
            language: {
                es: vdp_translation_es.js,
            },
            disabledDates: {
                to: dayjs('2020-05-20').toDate(),
                from: dayjs().toDate()
            }
        }
    },
    mounted () {
        this.getVariations();
    },
    methods: {
        getVariations: function(){
            let query = 'query MyQuery ($date:date){' +
                '   variation(order_by: {diff: desc}, where: {date: {_eq: $date}}) {' +
                '       date,productshopid,price,diff,product {name,url}' +
                '   }' +
                '}';

            const url = "http://ec2-3-17-64-92.us-east-2.compute.amazonaws.com:8085/v1/graphql";

            const opts = {
                method: "POST",
                headers: { "Content-Type": "application/json"},
                body: JSON.stringify({ query: query, variables: {"date":this.filterDate} })
            };

            fetch(url, opts)
                .then(res => res.json())
                .then(res => {this.prices = res.data.variation;})
                .catch(console.error);
        },
        formatPrice: function(number) {
            let val = (number/1).toFixed(2);
            return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        },
        getPercent: function(price, diff) {
            let previous = price - diff;

            if(previous == 0) return 0.00;

            return (diff / previous * 100).toFixed(2);
        },
        twoDecimals: function(number) {
            return number.toFixed(2);
        },
        getDiffClass: function(number) {
            if(number > 0) return 'diffPositive'

            return 'diffNegative'
        },
        openPicker: function() {
            this.$refs.programaticOpen.showCalendar();
            this.$refs.programaticOpen.$el.querySelector('input').focus();
        },
        dateSelected: function(date) {
            this.prices = [];
            this.filterDate = dayjs(date).format("YYYY-MM-DD");
            this.getVariations();
        }
    }
});