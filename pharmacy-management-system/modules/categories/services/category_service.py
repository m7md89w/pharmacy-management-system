from modules.categories.repository.category_repository import (
    CategoryRepository
)


class CategoryService:

    def __init__(
        self,
        category_repo: CategoryRepository
    ):
        self.category_repo = category_repo

    def create_category(
        self,
        data: dict
    ):

        existing = (
            self.category_repo.get_by_name(
                data["category_name"]
            )
        )

        if existing:
            raise ValueError(
                "Category already exists"
            )

        return self.category_repo.create(
            data
        )

    def get_category(
        self,
        category_id: int
    ):

        category = (
            self.category_repo.get_by_id(
                category_id
            )
        )

        if not category:
            raise ValueError(
                "Category not found"
            )

        return category

    def get_all_categories(self):

        return self.category_repo.get_all()

    def update_category(
        self,
        category,
        data: dict
    ):

        if "category_name" in data:

            existing = (
                self.category_repo.get_by_name(
                    data["category_name"]
                )
            )

            if (
                existing
                and existing.category_id
                != category.category_id
            ):
                raise ValueError(
                    "Category already exists"
                )

            category.category_name = data[
                "category_name"
            ]

        if "description" in data:
            category.description = data[
                "description"
            ]

        return self.category_repo.update(
            category
        )

    def delete_category(
        self,
        category
    ):

        return self.category_repo.delete(
            category
        )