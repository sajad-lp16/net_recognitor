# Generated by Django 2.2.4 on 2022-04-18 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, verbose_name="name")),
                (
                    "code",
                    models.CharField(max_length=5, null=True, verbose_name="code"),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="create time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="update time"),
                ),
            ],
            options={
                "verbose_name": "country",
                "verbose_name_plural": "countries",
                "db_table": "ip_ranges_country",
            },
        ),
        migrations.CreateModel(
            name="ISP",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(blank=True, max_length=100, verbose_name="name"),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="description"
                    ),
                ),
                (
                    "tags",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="tags"
                    ),
                ),
                (
                    "is_enable",
                    models.BooleanField(default=True, verbose_name="is enable"),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="create time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="update time"),
                ),
            ],
            options={
                "verbose_name": "isp",
                "verbose_name_plural": "isps",
                "db_table": "ip_manager_isp",
            },
        ),
        migrations.CreateModel(
            name="SourcePool",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("url", models.URLField()),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="create time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="update time"),
                ),
            ],
            options={
                "verbose_name": "source",
                "verbose_name_plural": "sources",
                "db_table": "ip_manager_source",
            },
        ),
        migrations.CreateModel(
            name="IpRange",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="city"
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="region"
                    ),
                ),
                (
                    "ip_network",
                    models.CharField(
                        blank=True, max_length=30, null=True, verbose_name="ip network"
                    ),
                ),
                (
                    "ip_from",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="ip from"
                    ),
                ),
                (
                    "ip_to",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="ip to"
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        choices=[(4, "IPV4"), (6, "IPV6")],
                        max_length=2,
                        verbose_name="version",
                    ),
                ),
                (
                    "is_enable",
                    models.BooleanField(default=True, verbose_name="is enable"),
                ),
                (
                    "expire_date",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="expire time"
                    ),
                ),
                (
                    "organization",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        null=True,
                        verbose_name="organization",
                    ),
                ),
                (
                    "address",
                    models.TextField(blank=True, null=True, verbose_name="address"),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=5,
                        max_digits=10,
                        null=True,
                        verbose_name="latitude",
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=5,
                        max_digits=10,
                        null=True,
                        verbose_name="longitude",
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="create time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="update time"),
                ),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ip_manager.Country",
                        verbose_name="country",
                    ),
                ),
                (
                    "isp",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ip_manager.ISP",
                        verbose_name="ISP",
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ip_manager.SourcePool",
                        verbose_name="source",
                    ),
                ),
            ],
            options={
                "verbose_name": "ip_range",
                "verbose_name_plural": "ip_ranges",
                "db_table": "ip_manager_ip_ranges",
            },
        ),
    ]
