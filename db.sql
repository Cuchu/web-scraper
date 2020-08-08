create table shop
(
    id   serial       not null
        constraint shop_pk
            primary key,
    name varchar(250) not null
);

alter table shop
    owner to postgres;

create unique index shop_id_uindex
    on shop (id);

create table product
(
    id            serial                 not null
        constraint product_pk
            primary key,
    productshopid varchar(250)           not null,
    category      varchar(250),
    name          varchar(250)           not null,
    url           varchar(250)           not null,
    shopid        integer      default 1 not null
        constraint product_shop_id_fk
            references shop,
    mcategory     varchar(250) default NULL::character varying,
    scategory     varchar(250) default NULL::character varying
);

alter table product
    owner to postgres;

create unique index product_url_uindex
    on product (url);

create unique index product_productshopid_uindex
    on product (productshopid);

create index product_scategory_index
    on product (scategory);

create table price
(
    id            serial                              not null,
    productid     integer
        constraint price_product_id_fk
            references product,
    productshopid varchar(250)   default NULL::character varying,
    date          date           default CURRENT_DATE not null,
    price         numeric(10, 2) default 0.00         not null
);

alter table price
    owner to postgres;

create index price_date_index
    on price (date desc);

create index price_productid_index
    on price (productid);

create index price_productshopid_index
    on price (productshopid);

create unique index price_productshopid_date_uindex
    on price (productshopid, date);

create table log
(
    id        serial       not null,
    category  varchar(250) not null,
    url       varchar(250),
    status    boolean default false,
    date      date    default CURRENT_DATE,
    mcategory varchar(250),
    scategory varchar(250)
);

alter table log
    owner to postgres;

create table variation
(
    productid     integer
        constraint variation_product_id_fk
            references product,
    productshopid varchar(250)   default NULL::character varying,
    date          date           default CURRENT_DATE not null,
    price         numeric(10, 2) default 0.00         not null,
    diff          numeric(10, 2) default 0.00         not null
);

alter table variation
    owner to postgres;

create index variation_date_index
    on variation (date desc);

create index variation_productid_index
    on variation (productid);

create table ipc_products
(
    productid integer
        constraint ipc_products_product_id_fk
            references product
);

alter table ipc_products
    owner to postgres;

create unique index ipc_products_productid_uindex
    on ipc_products (productid);

