import React, { Component } from "react";

import "../stylesheets/App.css";
import Question from "./Question";
import Search from "./Search";
import $ from "jquery";

class QuestionView extends Component {
    constructor() {
        super();
        this.state = {
            questions: [],
            page: 1,
            totalQuestions: 0,
            categories: {},
            currentCategory: null,
            filter: "all",
            query: "",
        };
    }

    componentDidMount() {
        this.getQuestions();
    }

    handleQuery = (search_term) => {
        this.setState({
            query: search_term,
        });
    };

    getQuestions = (page = 1) => {
        $.ajax({
            url: `/questions?page=${page}`, //TODO: update request URL
            type: "GET",
            success: (result) => {
                this.setState({
                    questions: result.questions,
                    totalQuestions: result.total_questions,
                    categories: result.categories,
                    currentCategory: result.current_category,
                    filter: "all",
                });
                return;
            },
            error: (error) => {
                alert(
                    "Unable to load questions. Please try your request again"
                );
                return;
            },
        });
    };

    selectPage(num) {
        this.setState(
            (prevState) => ({
                ...prevState,
                page: num,
            }),
            () => {
                switch (this.state.filter) {
                    case "all":
                        this.getQuestions(num);
                        break;
                    case "search":
                        this.submitSearch(this.state.query, num);
                        break;
                    case "category":
                        this.getByCategory(this.state.currentCategory, num);
                        break;
                }
            }
        );
    }

    createPagination() {
        let pageNumbers = [];
        let maxPage = Math.ceil(this.state.totalQuestions / 10);
        for (let i = 1; i <= maxPage; i++) {
            pageNumbers.push(
                <span
                    key={i}
                    className={`page-num ${
                        i === this.state.page ? "active" : ""
                    }`}
                    onClick={() => {
                        this.selectPage(i);
                    }}
                >
                    {i}
                </span>
            );
        }
        return pageNumbers;
    }

    getByCategory = (id, page = 1) => {
        $.ajax({
            url: `/categories/${id}/questions?page=${page}`, //TODO: update request URL
            type: "GET",
            success: (result) => {
                this.setState({
                    questions: result.questions,
                    totalQuestions: result.total_questions,
                    currentCategory: result.current_category,
                    filter: "category",
                });
                return;
            },
            error: (error) => {
                alert(
                    "Unable to load questions. Please try your request again"
                );
                return;
            },
        });
    };

    submitSearch = (searchTerm, page = 1) => {
        $.ajax({
            url: `/search`, //TODO: update request URL
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({ search_term: searchTerm, page }),
            xhrFields: {
                withCredentials: true,
            },
            crossDomain: true,
            success: (result) => {
                if (this.state.filter == "search") {
                    this.setState({
                        questions: result.questions,
                        totalQuestions: result.total_questions,
                        currentCategory: result.current_category,
                    });
                } else {
                    this.setState({
                        questions: result.questions,
                        totalQuestions: result.total_questions,
                        currentCategory: result.current_category,
                        page: 1,
                        filter: "search",
                    });
                }
                return;
            },
            error: (error) => {
                alert(
                    "Unable to load questions. Please try your request again"
                );
                return;
            },
        });
    };

    questionAction = (id) => (action) => {
        if (action === "DELETE") {
            if (
                window.confirm("are you sure you want to delete the question?")
            ) {
                $.ajax({
                    url: `/questions/${id}`, //TODO: update request URL
                    type: "DELETE",
                    success: (result) => {
                        this.getQuestions();
                    },
                    error: (error) => {
                        alert(
                            "Unable to load questions. Please try your request again"
                        );
                        return;
                    },
                });
            }
        }
    };

    render() {
        return (
            <div className="question-view">
                <div className="categories-list">
                    <h2
                        onClick={() => {
                            this.setState(
                                (prevState) => ({
                                    ...prevState,
                                    page: 1,
                                    filter: "all",
                                }),
                                () => this.getQuestions()
                            );
                        }}
                    >
                        Categories
                    </h2>
                    <ul>
                        {Object.keys(this.state.categories).map((id) => (
                            <li
                                key={id}
                                onClick={() => {
                                    this.setState(
                                        (prevState) => ({
                                            ...prevState,
                                            page: 1,
                                            filter: "category",
                                        }),
                                        () => this.getByCategory(id)
                                    );
                                }}
                            >
                                {this.state.categories[id]}
                                <img
                                    className="category"
                                    src={`${this.state.categories[id]}.svg`}
                                />
                            </li>
                        ))}
                    </ul>
                    <Search
                        submitSearch={this.submitSearch}
                        handleQuery={this.handleQuery}
                    />
                </div>
                <div className="questions-list">
                    <h2>Questions</h2>
                    {this.state.questions.map((q, ind) => (
                        <Question
                            key={q.id}
                            question={q.question}
                            answer={q.answer}
                            category={this.state.categories[q.category]}
                            difficulty={q.difficulty}
                            questionAction={this.questionAction(q.id)}
                        />
                    ))}
                    <div className="pagination-menu">
                        {this.createPagination()}
                    </div>
                </div>
            </div>
        );
    }
}

export default QuestionView;
