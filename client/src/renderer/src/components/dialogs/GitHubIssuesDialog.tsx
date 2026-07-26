import * as react from "react"
import * as Themes from "@radix-ui/themes"
import * as Popover from "@radix-ui/react-popover"

import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import rehypeHighlight from "rehype-highlight"

import "highlight.js/styles/github-dark.css"

import utility from "@renderer/common/utility"

import DialogRUI from "./DialogRUI"

const REPO: string = "https://api.github.com/repos/AlessioNegri/spacecraft-dynamics-lab"

const MILESTONE: string = "v0.2.0"

interface GitHubMilestone
{
    number: number
    title: string
}

interface GitHubIssue
{
    number: number
    title: string
    body: string
    labels:
    {
        name: string
    }[]
    milestone: GitHubMilestone
    html_url: string
    closed_at: string
}

/**
 * @description Formats a date string into a more readable format. If the date is null, it returns "Not closed".
 * 
 * @param date Date
 * @returns Formatted date string in the format "MMM DD, YYYY, HH:MM AM/PM" or "Not closed" if the date is null
 */
function formatDate(date: string | null): string
{
    if (!date) return "Not closed"
    
    return new Date(date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    })
}

const COLORS =
{
    enhancement: 'green',
    task: 'yellow'
}

interface Props
{
    opened: boolean
    setOpened: (opened: boolean) => void
}

/** @function GitHubIssuesDialog */
export default function GitHubIssuesDialog(props: Readonly<Props>): react.JSX.Element
{
    // --- HTTP ---

    async function loadIssues()
    {
        try
        {
            setLoading(true)

            const milestonesRes: Response = await fetch(`${REPO}/milestones`)

            const milestones: GitHubMilestone[] = await milestonesRes.json()

            const milestone: GitHubMilestone | undefined = milestones.find(m => m.title === MILESTONE)

            if (!milestone)
            {
                globalThis.window.api.warning(`Milestone ${MILESTONE} not found`)

                setIssues([])

                setLoading(false)

                return
            }

            const response: Response = await fetch(`${REPO}/issues?state=all&milestone=${milestone.number}`)

            const issuesRes: GitHubIssue[] = await response.json()

            setIssues(issuesRes.toSorted((a, b) => a.number - b.number))
        }
        catch (err)
        {
            globalThis.window.api.error(`Failed to fetch GitHub issues: ${err}`)
        }
        finally
        {
            setLoading(false)
        }
    }

    // --- USE STATE ---

    const [issues, setIssues] = react.useState<GitHubIssue[]>([])

    const [loading, setLoading] = react.useState<boolean>(true)

    // --- USE EFFECT ---

    react.useEffect(() =>
    {
        if (!props.opened) return

        loadIssues()
    }, [props.opened])

    // --- RENDERING ---

    return (
        <DialogRUI
            title="GitHub Issues"
            button="Close"
            open={props.opened}
            onClose={() => props.setOpened(false)}
            onSubmit={() => props.setOpened(false)}
        >

            {
                loading &&
                <Themes.Text size="3" className="text-neutral-400">
                    Loading issues…
                </Themes.Text>
            }

            {
                !loading && issues.length === 0 &&
                <Themes.Text size="3" className="text-neutral-400">
                    No implemented issues found.
                </Themes.Text>
            }

            <Themes.Flex direction="column" gap="4">
                
                {
                    issues.map(issue =>
                    <Themes.Flex
                        key={issue.number}
                        gap="4"
                        align="center"
                        direction="row"
                        className="bg-neutral-700/50 rounded p-4 select-text transition-colors hover:bg-neutral-600/50"
                    >
                        
                        <Themes.Box className="w-20 text-center">

                            <Themes.Text size="5" weight="bold" className="text-green-400">
                                #{issue.number}
                            </Themes.Text>

                        </Themes.Box>

                        <Themes.Flex direction="column" className="flex-1">

                            <Popover.Root>
                            
                                <Popover.Trigger asChild>
                    
                                    <Themes.Text
                                        size="4"
                                        weight="bold"
                                        className="pb-2 cursor-pointer hover:underline">
                                        {issue.title}
                                    </Themes.Text>
                    
                                </Popover.Trigger>
                    
                                <Popover.Portal>
                    
                                    <Popover.Content
                                        side="bottom"
                                        align="end"
                                        className={utility.cn("w-150 bg-neutral-900 border border-blue-400/50",
                                            "rounded-lg p-4 text-justify shadow-[0_0_20px_rgba(0,0,0,0.4)]",
                                            "text-sm text-neutral-200 leading-relaxed select-text")}
                                    >
                    
                                        <div className="space-y-2">

                                            <p className="font-semibold text-blue-300">{issue.title}</p>

                                            {/* <div className="prose prose-invert max-w-none"> */}
                                            <ReactMarkdown
                                                remarkPlugins={[remarkGfm]}
                                                rehypePlugins={[rehypeHighlight]}
                                            >
                                                {issue.body}
                                            </ReactMarkdown>
                                            {/* </div> */}
                                            
                                        </div>
                    
                                        <Popover.Arrow className="fill-blue-400/50" />
                    
                                    </Popover.Content>
                    
                                </Popover.Portal>
                                
                            </Popover.Root>

                            <Themes.Flex gap="2" className="pb-2">

                                {
                                    issue.labels.map(label =>
                                    <Themes.Badge
                                        key={label.name}
                                        color={COLORS[label.name]}
                                        className="px-2 py-1 rounded bg-neutral-600 text-neutral-200 text-xs"
                                    >
                                        {label.name}
                                    </Themes.Badge>
                                )}

                            </Themes.Flex>

                                <Themes.Text size="2" className="text-neutral-400 pb-1">
                                    Closed: {formatDate(issue.closed_at)}
                                </Themes.Text>

                            <Themes.Link
                                href={issue.html_url}
                                target="_blank"
                                className="text-orange-300 hover:text-orange-400"
                            >
                                View on GitHub →
                            </Themes.Link>

                        </Themes.Flex>

                    </Themes.Flex>
                )}

            </Themes.Flex>

        </DialogRUI>
    )
}
